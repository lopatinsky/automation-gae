# coding=utf-8
import logging

from methods import working_hours
from models import MenuItem, CARD_PAYMENT_TYPE


_MASTER_PROMO = {
    "id": "master",
    "text": u"Скидка на первый заказ картой MasterCard"
}

_CITY_HAPPY_HOURS = {
    "promo": {
        "id": "city_hh",
        "text": u"Счастливые часы: скидка 50р"
    },
    "venues": {
        5629499534213120: {
            "days": "12345",
            "hours": "20-21"
        }
    },
}


def _apply_master_promo(item_dicts, promos_info, client, payment_info):
    if payment_info["type_id"] == CARD_PAYMENT_TYPE and \
            payment_info["card"] == "mastercard" and \
            not client.has_mastercard_orders:
        promos_info.append(_MASTER_PROMO)

        most_expensive = None
        for item in item_dicts:
            if not most_expensive or most_expensive['price'] < item['price']:
                most_expensive = item

        most_expensive['promos'].append(_MASTER_PROMO['id'])
        most_expensive['price'] /= 2


def _apply_city_happy_hours_promo(item_dicts, promos_info, venue):
    if venue.key.id() in _CITY_HAPPY_HOURS['venues']:
        schedule = _CITY_HAPPY_HOURS['venues'][venue.key.id()]
        if working_hours.check(schedule['days'], schedule['hours']):
            promos_info.append(_CITY_HAPPY_HOURS['promo'])
            for item_dict in item_dicts:
                if item_dict['item'].price == 150:
                    logging.info(item_dict)
                    item_dict['promos'].append(_CITY_HAPPY_HOURS['promo']['id'])
                    item_dict['price'] -= 50


def _group_item_dicts(item_dicts):
    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'item': None}
        if item_dict['item'].key.id() == possible_group['item'] \
                and item_dict['price'] == possible_group['price'] \
                and item_dict['promos'] == possible_group['promos']:
            possible_group['quantity'] += 1
        else:
            result.append({
                'item': item_dict['item'].key.id(),
                'price': item_dict['price'],
                'promos': item_dict['promos'],
                'quantity': 1
            })
    return result


def validate_order(client, items, payment_info, venue):
    item_dicts = []
    for item in items:
        menu_item = MenuItem.get_by_id(int(item["id"]))
        for i in xrange(item["quantity"]):
            item_dicts.append({
                'item': menu_item,
                'price': menu_item.price,
                'promos': []
            })

    promos_info = []

    _apply_city_happy_hours_promo(item_dicts, promos_info, venue)
    _apply_master_promo(item_dicts, promos_info, client, payment_info)

    total_sum = 0
    for item_dict in item_dicts:
        total_sum += item_dict['price']

    grouped_item_dicts = _group_item_dicts(item_dicts)

    return {
        'valid': True,
        'items': grouped_item_dicts,
        'promos': promos_info,
        'total_sum': total_sum
    }
