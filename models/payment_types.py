# coding=utf-8
CASH_PAYMENT_TYPE = 0
CARD_PAYMENT_TYPE = 1
PAYPAL_PAYMENT_TYPE = 4
PAYMENT_TYPE_CHOICES = (CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE)

PAYMENT_TYPE_MAP = {
    CARD_PAYMENT_TYPE: u"Карта",
    CASH_PAYMENT_TYPE: u"Наличными",
    PAYPAL_PAYMENT_TYPE: u'Paypal'
}

from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES


class PaymentType(ndb.Model):  # self.key.id() == type
    title = ndb.StringProperty(indexed=False)  # todo: why?
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def fetch_types(cls, *args, **kwargs):
        from config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.payment_types import get_payment_types
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return cls.query(*args, **kwargs).fetch()
        elif app_kind == RESTO_APP:
            types = get_payment_types()
            for type in types[:]:
                for name, value in kwargs.items():
                    if getattr(type, name) != value:
                        types.remove(type)
            return types

    def dict(self):
        dct = {
            'id': int(self.key.id()),
            'title': self.title
        }
        return dct
