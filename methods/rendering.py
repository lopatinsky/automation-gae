# coding=utf-8
import time


STR_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STR_DATE_FORMAT = "%Y-%m-%d"
STR_TIME_FORMAT = "%H:%M"

HTML_STR_TIME_FORMAT = "%Y-%m-%dT%H:%M"


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