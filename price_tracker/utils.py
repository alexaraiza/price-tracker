from datetime import datetime
import re


def get_regex_string_from_number(number):
    integer = int(number)
    integer_string = str(integer)
    string = ""
    for digit in integer_string:
        string += f"{digit}[.,' ]?"
    if number == integer:
        return string[0:-7]
    string = string[0:-1]
    decimal_string = str((round(1000000*number) - 1000000*integer)/1000000)[2:]
    for digit in decimal_string:
        string += digit
    return string


def get_relevant_attributes(element, price_regex_string):
    attributes = {}
    for attribute in element.attrs:
        if attribute in ["style", "viewbox"]:
            continue
        attribute_value = element[attribute]
        if type(attribute_value) == list:
            attribute_list = []
            for value in attribute_value:
                match = re.search(price_regex_string, value)
                if not match:
                    attribute_list.append(value)
            if attribute_list:
                attributes[attribute] = attribute_list
        else:
            match = re.search(price_regex_string, attribute_value)
            if not match:
                attributes[attribute] = attribute_value
    return attributes


def get_float_from_string(string):
    separators = re.findall("[.,' ]", string)
    if not separators:
        return float(string)
    last_separator = separators.pop()
    if last_separator in separators:
        string = re.sub("[.,' ]", "", string)
        return float(string)
    string = string.replace("_", "")
    string = re.sub("[.,' ]", "_", string)
    last_underscore_index = string.rindex("_")
    string = f"{string[0:last_underscore_index]}.{string[last_underscore_index+1:len(string)]}"
    return float(string)


def price_is_in_string(price, string):
    price_is_in_string = False
    matches = re.findall("\d[.,' \d]*\d|\d", string)
    for price_string in matches:
        try:
            if get_float_from_string(price_string) == price:
                price_is_in_string = True
                break
        except ValueError:
            continue
    return price_is_in_string


def get_prices_from_elements(elements):
    prices = {}
    most_common_prices = []
    max_times = 0
    for element in elements:
        for string in element.strings:
            matches = re.findall("\d[.,' \d]*\d|\d", string)
            for price_string in matches:
                try:
                    price = get_float_from_string(price_string)
                except ValueError:
                    continue
                if price in prices:
                    prices[price] += 1
                else:
                    prices[price] = 1
                if prices[price] > max_times:
                    most_common_prices = [price]
                    max_times = prices[price]
                elif prices[price] == max_times:
                    most_common_prices.append(price)
    return most_common_prices


def get_months_between(then, now):
    return 12*(now.year - then.year) + now.month - then.month - (get_time_since_month_start(now) < get_time_since_month_start(then))


def get_time_since_month_start(datetime_):
    return datetime_ - datetime(datetime_.year, datetime_.month, 1)