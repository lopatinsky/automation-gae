from google.appengine.api import memcache
from methods.proxy.doubleb.requests import get_doubleb_payment_types
from models import PaymentType, STATUS_AVAILABLE
from models.payment_types import CARD_PAYMENT_TYPE, CASH_PAYMENT_TYPE
from models.proxy.doubleb import DoublebCompany

__author__ = 'dvpermyakov'

PAYMENT_TYPE_MAP = {
    0: str(CASH_PAYMENT_TYPE),
    1: str(CARD_PAYMENT_TYPE)
}


def get_payment_types():
    payment_types = memcache.get('doubleb_payment_types')
    if not payment_types:
        company = DoublebCompany.get()
        payment_type_dicts = get_doubleb_payment_types(company)
        payment_types = []
        for payment_type_dict in payment_type_dicts['payment_types']:
            if PAYMENT_TYPE_MAP.get(payment_type_dict['id']) == None:
                continue
            payment_type = PaymentType(id=PAYMENT_TYPE_MAP[payment_type_dict['id']])
            payment_type.title = payment_type_dict['title']
            payment_type.status = STATUS_AVAILABLE
            payment_types.append(payment_type)
        memcache.set('doubleb_payment_types', payment_types, 3600)
    return payment_types


def get_payment_type(payment_id):
    for payment_type in get_payment_types():
        if payment_type.key.id() == payment_id:
            return payment_type
