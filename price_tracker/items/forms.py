from flask_wtf import FlaskForm

import re

from wtforms.fields import BooleanField, RadioField, SelectField, StringField, SubmitField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Optional, StopValidation, URL, ValidationError

from currencies import currencies, currency_list_xe_singular
from price_tracker.models import PRICE_MULTIPLIER
from price_tracker.utils import get_float_from_string


NOTIFICATION_CHOICES = [
    "When price changes",
    "When price is lower than target price"
]

NOTIFICATION_CHOICES_REQUIRING_TARGET_PRICE = [
    "When price is lower than target price"
]


def validate_price(form, field):
    match = re.fullmatch("\d[.,' \d]*\d|\d", field.data)
    if not match:
        raise ValidationError("Invalid price")

def validate_notification_choice(form, field):
    if form.notify_user.data and not field.data:
        raise StopValidation()

def validate_target_price(form, field):
    if form.notify_user.data and form.notification_choice.data in NOTIFICATION_CHOICES_REQUIRING_TARGET_PRICE and not field.data:
        raise StopValidation("Target price required")


class ItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Name required")])
    url = URLField("URL", validators=[DataRequired(message="URL required"), URL(message="Invalid URL")])
    current_price = StringField("Current price", validators=[Optional(), validate_price])
    currency = SelectField(choices=[('', 'Select currency...')]+currency_list_xe_singular, validators=[DataRequired(message="Currency required")])
    notify_user = BooleanField("Notify me")
    notification_choice = RadioField(choices=NOTIFICATION_CHOICES, validators=[validate_notification_choice, Optional()])
    target_price = StringField("Target price", validators=[validate_target_price, Optional(), validate_price])

    def get_price(self, field):
        if not field.data:
            return None
        if field is self.target_price:
            if not self.notify_user.data or self.notification_choice.data not in NOTIFICATION_CHOICES_REQUIRING_TARGET_PRICE:
                return None
        price = get_float_from_string(field.data)
        decimal_multiplier = 10 ** currencies[self.currency.data]["minor unit"]
        return PRICE_MULTIPLIER * round(decimal_multiplier * price) // decimal_multiplier

    def get_notification_choice(self):
        if self.notify_user.data:
            return NOTIFICATION_CHOICES.index(self.notification_choice.data)
        return -1

class EditItemForm(ItemForm):
    submit = SubmitField("Save item")

class NewItemForm(ItemForm):
    submit = SubmitField("Add item")