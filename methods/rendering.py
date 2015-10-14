# coding=utf-8
from datetime import datetime
import time
import re
from models.client import ANDROID_DEVICE, IOS_DEVICE

STR_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STR_DATE_FORMAT = "%Y-%m-%d"
STR_TIME_FORMAT = "%H:%M"

HTML_STR_TIME_FORMAT = "%Y-%m-%dT%H:%M"

AM_PM_STR_DATETIME_FORMAT = "%Y-%m-%d %I:%M:%S %p"
BUGGED_DATETIME_FORMAT = "%Y-%m-%d %H%I:%M:%S %p"


def timestamp(datetime_object):
    return int(time.mktime(datetime_object.timetuple()))


def latinize(name):
    english = u'abcdefghijklmnopqrstuvwxyz'
    russian = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    russian_translate = u'abvgdeezziiklmnoprstufhchhhiiiaua'
    new_name = u''
    for letter in name.lower():
        if letter in russian:
            new_name += russian_translate[russian.index(letter)]
        else:
            if letter in english:
                new_name += letter
    return new_name


def get_phone(phone_str):
    return re.sub("[^0-9]", "", phone_str)


def sms_phone(phone):
    if len(phone) == 11 and phone[0] == "8":
        phone = "7" + phone[1:]
    return phone


def get_separated_name_surname(name_and_surname):
    values = name_and_surname.split(None, 1)
    if not values:
        return '', ''
    elif len(values) == 1:
        return values[0], ''
    else:
        return values[0], values[1]


def parse_time_picker_value(time_picker_value):
    try:
        return datetime.strptime(time_picker_value, STR_DATETIME_FORMAT)
    except ValueError:
        try:
            return datetime.strptime(time_picker_value, AM_PM_STR_DATETIME_FORMAT)
        except ValueError:
            return datetime.strptime(time_picker_value, BUGGED_DATETIME_FORMAT)


def get_device_type(user_agent):
    if 'Android' in user_agent:
        return ANDROID_DEVICE
    else:
        return IOS_DEVICE
