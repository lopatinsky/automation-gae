from config import Config
from models import PaymentType
from requests import get_iiko_payment_types

__author__ = 'dvpermyakov'


def get_payment_types():
    config = Config.get()
    iiko_company = config.IIKO_COMPANY.get()
    iiko_payment_types = get_iiko_payment_types(iiko_company)
    payment_types = []
    for iiko_payment_type in iiko_payment_types['types']:
        payment_type = PaymentType()
        payment_type.faked_id = iiko_payment_type['type_id']
        payment_type.title = iiko_payment_type['name']
        payment_type.status = int(iiko_payment_type['available'])
        payment_types.append(payment_type)
    return payment_types
