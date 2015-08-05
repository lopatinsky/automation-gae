from config import Config
from methods.proxy.resto.requests import get_resto_delivery_types
from models.venue import DeliveryType, DELIVERY, SELF

__author__ = 'dvpermyakov'

DELIVERY_TYPE_MAP = {
    'self': SELF,
    'delivery': DELIVERY
}


def get_delivery_types():
    config = Config.get()
    resto_company = config.RESTO_COMPANY.get()
    resto_delivery_types = get_resto_delivery_types(resto_company)
    delivery_types = []
    for resto_deliery_type in resto_delivery_types['types']:
        delivery_type = DeliveryType()
        delivery_type.delivery_type = DELIVERY_TYPE_MAP[resto_deliery_type['name']]
        delivery_type.status = resto_deliery_type['available']
        delivery_types.append(delivery_type)
    return delivery_types
