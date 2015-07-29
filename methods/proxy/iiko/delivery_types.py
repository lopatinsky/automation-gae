from config import Config
from methods.proxy.iiko.requests import get_iiko_delivery_types
from models.venue import DeliveryType, DELIVERY, SELF

__author__ = 'dvpermyakov'


def get_delivery_types():
    config = Config.get()
    iiko_company = config.IIKO_COMPANY.get()
    iiko_delivery_types = get_iiko_delivery_types(iiko_company)
    delivery_types = []
    for iiko_deliery_type in iiko_delivery_types['types']:
        delivery_type_id = None
        if iiko_deliery_type['name'] == 'self':
            delivery_type_id = SELF
        elif iiko_deliery_type['name'] == 'delivery':
            delivery_type_id = DELIVERY
        if delivery_type_id is not None:
            delivery_type = DeliveryType()
            delivery_type.delivery_type = delivery_type_id
            delivery_type.status = iiko_deliery_type['available']
            delivery_types.append(delivery_type)
    return delivery_types
