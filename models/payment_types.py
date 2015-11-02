# coding=utf-8
CASH_PAYMENT_TYPE = 0
CARD_PAYMENT_TYPE = 1
PAYPAL_PAYMENT_TYPE = 4
CARD_COURIER_PAYMENT_TYPE = 5
PAYMENT_TYPE_CHOICES = (CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE, CARD_COURIER_PAYMENT_TYPE)

PAYMENT_TYPE_MAP = {
    CARD_PAYMENT_TYPE: u"Карта",
    CASH_PAYMENT_TYPE: u"Наличными",
    PAYPAL_PAYMENT_TYPE: u'Paypal',
    CARD_COURIER_PAYMENT_TYPE: u'Карта Курьеру'
}

from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES


class PaymentType(ndb.Model):  # self.key.id() == type
    title = ndb.StringProperty(indexed=False)  # todo: why?
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def get(cls, payment_id):
        from models.config.config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.payment_types import get_payment_type
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            return cls.get_by_id(str(payment_id))
        elif app_kind == RESTO_APP:
            return get_payment_type(str(payment_id))

    @classmethod
    def fetch_types(cls, **kwargs):
        from models.config.config import Config, AUTO_APP, RESTO_APP
        from methods.proxy.resto.payment_types import get_payment_types
        app_kind = Config.get().APP_KIND
        if app_kind == AUTO_APP:
            filters = []
            for prop_name, value in kwargs.items():
                filters.append(getattr(PaymentType, prop_name) == value)
            return cls.query(*filters).fetch()
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
            'title': self.title,
            'really_title': PAYMENT_TYPE_MAP[int(self.key.id())]
        }
        return dct
