from datetime import datetime
from methods.orders.validation.validation import get_response_dict, set_modifiers, set_price_with_modifiers, \
    set_item_dicts
from methods.proxy.doubleb.requests import post_doubleb_check_order
from models.proxy.doubleb import DoublebCompany, DoublebClient

__author__ = 'dvpermyakov'


def get_doubleb_delivery_time(delivery_time):
    return int((delivery_time - datetime.utcnow()).seconds / 60)


def update_payment_info(payment_info):
    payment_info.update({
        'mastercard': False
    })
    return payment_info


def get_auto_item_dicts(items):
    items = set_modifiers(items)
    items = set_price_with_modifiers(items)
    item_dicts = set_item_dicts(items)
    return item_dicts


def get_doubleb_item_dicts(items):
    item_dicts = []
    for item in items:
        item_dicts.append({
            'item_id': item['item_id'],
            'quantity': item['quantity']
        })
    return item_dicts


def doubleb_validate_order(client, venue, items, payment_info, delivery_time):
    company = DoublebCompany.get()
    doubleb_client = DoublebClient.get(client)
    doubleb_validation = post_doubleb_check_order(company, doubleb_client, venue,
                                                  get_doubleb_item_dicts(items),
                                                  update_payment_info(payment_info),
                                                  get_doubleb_delivery_time(delivery_time))
    required_value = {
        'valid': doubleb_validation['valid'],
        'error': doubleb_validation['errors'],
        'total_sum': doubleb_validation['total_sum'],
        'item_dicts': get_auto_item_dicts(items),
        'promos': doubleb_validation['promos']
    }
    response = get_response_dict(**required_value)
    return response
