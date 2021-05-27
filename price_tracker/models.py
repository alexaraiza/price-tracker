from flask_login import UserMixin

from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from requests.exceptions import Timeout

from price_tracker import db, login_manager
import price_tracker.utils as utils
from price_tracker.webpages import get_response_text
from currencies import currencies


class PriceResolutionError(Exception):
    """Raised when price is not resolved"""
    def __init__(self, message, price_list):
        self.message = message
        self.price_list = price_list
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} from {self.price_list}"


PRICE_MULTIPLIER = 1000


TIME_MULTIPLES = {
    "day": {
        "weeks": 7,
        "days": 1
    },
    "second": {
        "hours": 3600,
        "minutes": 60,
        "seconds": 1
    }
}

MONTH_MULTIPLES = {
    "years": 12,
    "months": 1
}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    signup_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_demo_user = db.Column(db.Boolean, nullable=False)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)
    items = db.relationship("Item", backref="user", lazy=True)

    def get_all_prices(self):
        prices = []
        for item in self.items:
            try:
                price = item.get_price()
            except PriceResolutionError:
                price = None
            prices.append(price)
        return prices


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240), nullable=False)
    url = db.Column(db.String(2000), nullable=False)
    current_price = db.Column(db.Integer)
    last_update_datetime = db.Column(db.DateTime)
    price_history = db.Column(db.String(2000), nullable=False, default="[]")
    currency = db.Column(db.String(3), nullable=False)
    notification_choice = db.Column(db.Integer, nullable=False, default=-1)
    target_price = db.Column(db.Integer)
    elements = db.Column(db.String(2000), nullable=False, default="[]")
    creation_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def add_to_price_history(self, price):
        price_history = json.loads(self.price_history)
        price_history.append(price)
        if (len(price_history) > 120):
            price_history.pop(0)
        self.price_history = json.dumps(price_history, separators=(',', ':'))

    def get_time_since_last_update(self):
        now = datetime.utcnow()
        time_passed = now - self.last_update_datetime
        time_multiple_count = {"day": time_passed.days, "second": time_passed.seconds}
        if time_passed.days < 28:
            for time_multiple, UNITS in TIME_MULTIPLES.items():
                time_multiples_passed = time_multiple_count[time_multiple]
                for unit, time_multiples_per_unit in UNITS.items():
                    unit_count = time_multiples_passed // time_multiples_per_unit
                    if unit_count > 1:
                        return f"{unit_count} {unit}"
                    if unit_count == 1:
                        return f"{unit_count} {unit[0:-1]}"
            return "0 seconds"
        months_passed = utils.get_months_between(self.last_update_datetime, now)
        for unit, time_multiples_per_unit in MONTH_MULTIPLES.items():
            unit_count = months_passed // time_multiples_per_unit
            if unit_count > 1:
                return f"{unit_count} {unit}"
            if unit_count == 1:
                return f"{unit_count} {unit[0:-1]}"
        return "4 weeks"

    def get_price_string(self, price, with_currency=True):
        currency = currencies[self.currency]
        price_string_without_currency = f"{(price / PRICE_MULTIPLIER):.{currency['minor unit']}f}"
        return f"{self.currency}{price_string_without_currency}" if with_currency else price_string_without_currency

    def get_elements(self):
        try:
            response = get_response_text(self.url)
        except Timeout:
            response = ""
        item_price = self.current_price / PRICE_MULTIPLIER
        price_regex_string = utils.get_regex_string_from_number(item_price)
        soup = BeautifulSoup(response, "html5lib")
        strings = soup.find_all(string=re.compile(price_regex_string))
        if not strings:
            response = get_response_text(self.url, "selenium")
            soup = BeautifulSoup(response, "html5lib")
            strings = soup.find_all(string=re.compile(price_regex_string))
            if not strings:
                raise ValueError(f"no elements matching '{price_regex_string}' found")
        elements = []
        for string in strings:
            element = string.parent
            if element.name in ("script", "style") or not utils.price_is_in_string(item_price, string):
                continue
            attributes = utils.get_relevant_attributes(element, price_regex_string)
            if not attributes:
                continue
            similar_elements = soup.find_all(attrs=attributes)
            indices = [i for i in range(len(similar_elements)) if similar_elements[i] == element]
            element_object = {"attr": attributes, "i": indices}
            if element_object not in elements:
                elements.append(element_object)
        return elements

    def get_price(self):
        elements_to_search = json.loads(self.elements)
        if not elements_to_search:
            return None
        method = "requests"
        most_common_prices = []
        while not most_common_prices:
            try:
                response = get_response_text(self.url, method)
            except Timeout:
                method = "selenium"
                continue
            soup = BeautifulSoup(response, "html5lib")
            elements_found = []
            for element in elements_to_search:
                for i in element["i"]:
                    try:
                        elements_found.append(soup.find_all(attrs=element["attr"])[i])
                    except IndexError:
                        pass
            most_common_prices = utils.get_prices_from_elements(elements_found)
            if not most_common_prices and method == "selenium":
                return None
            method = "selenium"
        most_common_prices = [round(PRICE_MULTIPLIER * price) for price in most_common_prices]
        if len(most_common_prices) == 1:
            return most_common_prices[0]
        if self.current_price:
            return min(most_common_prices, key=lambda price: abs(self.current_price - price))
        raise PriceResolutionError("could not determine the correct price", most_common_prices)