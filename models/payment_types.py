# coding=utf-8
CASH_PAYMENT_TYPE = 0
CARD_PAYMENT_TYPE = 1
PAYPAL_PAYMENT_TYPE = 4
PAYMENT_TYPE_CHOICES = [CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE]

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

    def dict(self):
        dct = {
            'id': int(self.key.id()),
            'title': self.title
        }
        return dct