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
from models import STATUS_AVAILABLE, STATUS_UNAVAILABLE


class PaymentType(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    status = ndb.IntegerProperty(required=True, choices=(STATUS_AVAILABLE, STATUS_UNAVAILABLE),
                                 default=STATUS_AVAILABLE)

    @classmethod
    def fetch_types(cls, app_kind, *args, **kwargs):
        from config import AUTO_APP, IIKO_APP
        from methods.proxy.iiko.payment_types import get_payment_types
        if app_kind == AUTO_APP:
            return cls.query(*args, **kwargs).fetch()
        elif app_kind == IIKO_APP:
            types = get_payment_types()
            for type in types[:]:
                for name, value in kwargs.items():
                    if getattr(type, name) != value:
                        types.remove(type)
            return types

    def dict(self):
        dct = {
            'id': int(self.key.id()) if hasattr(self.key, 'id') else self.faked_id,
            'title': self.title
        }
        return dct