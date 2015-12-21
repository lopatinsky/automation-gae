# coding=utf-8
from google.appengine.ext import ndb

from models import STATUS_AVAILABLE, STATUS_CHOICES, STATUS_MAP

__author__ = 'dvpermyakov'

WITHOUT_CONDITIONS = 0
REPEATED_ORDER_CONDITIONS = 1  # если один раз заказал, а потом не заказывал
REPEATED_ORDER_ONE_USE_CONDITION = 2  # если один раз заказал, а потом не заказывал
ORDER_IN_ONE_DAY = 3  # достает клиентов, которые заказывали последний раз N дней назад



# новым юзерам, если они не делали в течении N дней заказ
# которые заказали один раз и n дней не делали заказ



NEW_USERS_WITH_NO_ORDERS = 0
USERS_WITH_ONE_ORDER = 1
NOT_TYPES = (NEW_USERS_WITH_NO_ORDERS, USERS_WITH_ONE_ORDER)


NOT_TYPES_MAP = {
    NEW_USERS_WITH_NO_ORDERS: u'Новые неактивные клиенты',
    USERS_WITH_ONE_ORDER: u'Неактивные клиенты с одним заказом',
}

CONDITIONS = (WITHOUT_CONDITIONS, REPEATED_ORDER_CONDITIONS, REPEATED_ORDER_ONE_USE_CONDITION, ORDER_IN_ONE_DAY)


class NotificatingInactiveUsersModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    header = ndb.StringProperty(required=True)
    text = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=NOT_TYPES)
    days = ndb.IntegerProperty(required=True)
    should_push = ndb.BooleanProperty(default=False)
    should_sms = ndb.BooleanProperty(default=False)
    sms_if_has_points = ndb.BooleanProperty(default=False)
    sms_if_has_cashback = ndb.BooleanProperty(default=False)
    already_sent = ndb.BooleanProperty(default=False)