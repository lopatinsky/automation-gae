from methods.orders.validation.validation import get_response_dict, set_modifiers, set_price_with_modifiers, \
    set_item_dicts
from models.proxy.resto import RestoClient
from requests import post_resto_check_order

__author__ = 'dvpermyakov'


def get_resto_address_dict(address):
    return {
        'city': address.city,
        'street': address.street,
        'home': address.home,
        'apartment': address.flat,
        'entrance': '-',
        'housing': '-',
        'floor': '-'
    }


def _get_init_total_sum(items):
    total_sum = 0
    for item in items:
        total_sum += item.total_price
    return total_sum


def get_item_and_item_dicts(items):
    items = set_modifiers(items)
    items = set_price_with_modifiers(items)
    item_dicts = set_item_dicts(items)
    return items, item_dicts


def get_resto_item_dicts(init_item_dicts):
    return [{
        'id': item_dict['item_id'],
        'name': '',
        'amount': item_dict['quantity']
    } for item_dict in init_item_dicts]


def resto_validate_order(client, init_item_dicts, venue, delivery_time):
    items, item_dicts = get_item_and_item_dicts(init_item_dicts)
    total_sum = _get_init_total_sum(items)
    resto_client = RestoClient.get(client)
    resto_item_dicts = get_resto_item_dicts(init_item_dicts)
    resto_validation = post_resto_check_order(venue, resto_item_dicts, client, resto_client, total_sum, delivery_time)
    required_value = {
        'valid': not resto_validation['error'],
        'error': resto_validation['description'] if resto_validation['error'] else None,
        'total_sum': total_sum,
        'item_dicts': item_dicts
    }
    updated_value = {}
    response = get_response_dict(**required_value)
    response.update(updated_value)
    return response
