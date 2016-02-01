# coding=utf-8
from google.appengine.ext import ndb

__author__ = 'Artem'

DELIVERY_TYPE = 0

MESSAGE_CONDITIONS = (DELIVERY_TYPE,)

MESSAGE_CONDITIONS_MAP = {
    DELIVERY_TYPE: u"Тип доставки"
}

DISABLED = 0
ENABLED = 1

STATUSES = (ENABLED, DISABLED)


class Condition(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUSES, required=True)
    type = ndb.IntegerProperty(choices=MESSAGE_CONDITIONS, required=True)
    messages = ndb.StringProperty(repeated=True)

    @property
    def name(self):
        if self.type == None:
            return u"Неопределено"
        else:
            return MESSAGE_CONDITIONS_MAP[self.type]
        pass

    def set_messages(self, *args):
        self.messages = args


class OrderMessageModule(ndb.Model):
    condition = ndb.KeyProperty(kind=Condition)
    default_message = ndb.StringProperty()
    status = ndb.IntegerProperty(choices=STATUSES, required=True)

    def get_message(self, order):

        if not self.condition:
            return self.default_message

        if self.condition.get().type == DELIVERY_TYPE:
            return self.condition.get().messages[order.delivery_type]

        return self.default_message
