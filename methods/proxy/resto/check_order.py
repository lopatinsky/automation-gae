import logging
from methods.orders.validation.validation import get_response_dict, set_modifiers, set_price_with_modifiers, \
    set_item_dicts, group_item_dicts, is_equal
from models.proxy.resto import RestoClient, RestoCompany
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


def get_init_total_sum(items):
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
    item_dicts = []
    for item_dict in init_item_dicts:
        modifiers = [{
            'groupId': modifier['group_modifier_id'],
            'groupName': '',
            'id': modifier['choice'],
            'name': '',
            'amount': modifier['quantity']
        } for modifier in item_dict['group_modifiers']]
        modifiers.extend([{
            'id': modifier['single_modifier_id'],
            'name': '',
            'amount': modifier['quantity']
        } for modifier in item_dict['single_modifiers']])
        item_dicts.append({
            'id': item_dict['item_id'],
            'name': '',
            'amount': item_dict['quantity'],
            'modifiers': modifiers
        })
    return item_dicts


def get_item_dicts_by_resto(resto_item_dicts):
    items = [{
        'item_id': resto_item_dict['id'],
        'single_modifiers': [],
        'group_modifiers': [],
        'quantity': 1
    } for resto_item_dict in resto_item_dicts]
    items, item_dicts = get_item_and_item_dicts(items)
    return item_dicts


def get_new_and_unaval_gifts(order_gifts_from_resto, order_gift_dicts, cancelled_order_gifts):
    new_order_gifts = []
    for order_gift_from_resto in order_gifts_from_resto:
        found = False
        for gift in order_gift_dicts:
            if is_equal(order_gift_from_resto, gift):
                gift['found'] = True
                found = True
        for gift in cancelled_order_gifts:
            if is_equal(order_gift_from_resto, gift):
                gift['found'] = True
                found = True
        if not found:
            new_order_gifts.append(order_gift_from_resto)
    unavail_order_gifts = []
    for gift in order_gift_dicts:
        if not gift.get('found', False):
            unavail_order_gifts.append(gift)
    return new_order_gifts, unavail_order_gifts


def resto_validate_order(client, init_item_dicts, venue, delivery_time, order_gifts, cancelled_order_gifts,
                         delivery_type):
    resto_company = RestoCompany.get()
    items, item_dicts = get_item_and_item_dicts(init_item_dicts)
    order_gifts, order_gift_dicts = get_item_and_item_dicts(order_gifts)
    cancelled_order_gifts, cancelled_order_gift_dicts = get_item_and_item_dicts(cancelled_order_gifts)
    total_sum = get_init_total_sum(items)
    resto_client = RestoClient.get(client)
    resto_item_dicts = get_resto_item_dicts(init_item_dicts)
    resto_validation = post_resto_check_order(resto_company, venue, resto_item_dicts, client, resto_client, total_sum,
                                              delivery_time, delivery_type)
    order_gifts_from_resto = get_item_dicts_by_resto(resto_validation.get('gifts', []))
    new_order_gifts, unavail_order_gifts = get_new_and_unaval_gifts(order_gifts_from_resto, order_gift_dicts,
                                                                    cancelled_order_gifts)
    required_value = {
        'valid': not resto_validation['error'],
        'error': resto_validation['description'] if resto_validation['error'] else None,
        'total_sum': total_sum - resto_validation.get('order_discounts', 0),
        'item_dicts': item_dicts,
    }
    response = get_response_dict(**required_value)
    if response['valid']:
        updated_value = {
            'max_wallet_payment': resto_validation['max_bonus_payment'],
            'wallet_balance': resto_validation['balance'],
            'wallet_cash_back': 0,
            'new_order_gifts': group_item_dicts(new_order_gifts),
            'unavail_order_gifts': group_item_dicts(unavail_order_gifts),
            'order_gifts': group_item_dicts(order_gift_dicts),
            'cancelled_order_gifts': group_item_dicts(cancelled_order_gifts),
        }
        response.update(updated_value)
    logging.info('response = %s' % response)
    return response
