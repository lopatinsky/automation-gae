from models import PaymentType
from models.payment_types import CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE
from models.proxy.resto import RestoCompany
from requests import get_resto_payment_types

__author__ = 'dvpermyakov'

PAYMENT_TYPE_MAP = {
    1: str(CASH_PAYMENT_TYPE),
    2: str(CARD_PAYMENT_TYPE)
}

REVERSE_PAYMENT_TYPE_MAP = {
    CASH_PAYMENT_TYPE: 1,
    CARD_PAYMENT_TYPE: 2
}


def get_payment_types():
    resto_company = RestoCompany.get()
    resto_payment_types = get_resto_payment_types(resto_company)
    payment_types = []
    for resto_payment_type in resto_payment_types['types']:
        payment_type = PaymentType(id=PAYMENT_TYPE_MAP[resto_payment_type['type_id']])
        payment_type.title = resto_payment_type['name']
        payment_type.status = int(resto_payment_type['available'])
        payment_types.append(payment_type)
    return payment_types


def get_payment_type(payment_id):
    for payment_type in get_payment_types():
        if payment_type.key.id() == payment_id:
            return payment_type