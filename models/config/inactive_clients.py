# coding=utf-8
from google.appengine.ext import ndb

from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'aryabukha'

CALENDAR = 0
WITH_CASHBACK = 1
N_POINTS_LEFT = 2
NO_ORDERS = 3
LEFT_BASKET = 4
NEW_USER = 5

NOTIFICATION_TYPES = (WITH_CASHBACK, N_POINTS_LEFT, NO_ORDERS, NEW_USER)

NOTIFICATION_TYPES_MAP = {
    # WITH_CASHBACK: u'Есть накопленные баллы по кэшбеку',
    # N_POINTS_LEFT: u'Осталось N баллов до подарка',
    NO_ORDERS: u'Не делавшие заказ N дней',
    NEW_USER: u'Новый пользователь без заказа N дней'
}

CONDITIONS_MAP = {
    # WITH_CASHBACK: u'Баллы по кэшбеку',
    # N_POINTS_LEFT: u'Баллов до подарка',
    NO_ORDERS: u'Дней без заказа',
    NEW_USER: u'Дней без заказа'
}


class InactiveNotificationModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    header = ndb.StringProperty(required=True)
    conditions = ndb.JsonProperty()
    type = ndb.IntegerProperty(required=True, choices=NOTIFICATION_TYPES)
    should_push = ndb.BooleanProperty(default=False)
    should_sms = ndb.BooleanProperty(default=False)
    sms_if_has_points = ndb.BooleanProperty(default=False)
    sms_if_has_cashback = ndb.BooleanProperty(default=False)
    needed_cashback = ndb.IntegerProperty(default=None)
    needed_points_left = ndb.IntegerProperty(default=None)
