from methods.proxy.doubleb.requests import get_doubleb_payment_types
from models import PaymentType, STATUS_AVAILABLE
from models.payment_types import CARD_PAYMENT_TYPE
from models.proxy.doubleb import DoublebCompany

__author__ = 'dvpermyakov'

PAYMENT_TYPE_MAP = {
    1: str(CARD_PAYMENT_TYPE)
}


def get_payment_types():
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
    return payment_types
