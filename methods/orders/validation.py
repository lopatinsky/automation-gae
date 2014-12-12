# coding=utf-8
import logging
import datetime
from config import config

from methods import working_hours
from models import MenuItem, CARD_PAYMENT_TYPE


_MASTER_PROMO = {
    "id": "master",
    "text": u"Скидка 50% на один напиток при первом заказе картой MasterCard"
}

_CITY_HAPPY_HOURS_PROMO = {
    "id": "city_hh",
    "text": u"Счастливые часы: скидка 50р"
}


def _check_venue(venue, delivery_time, errors):
    if venue:
        if not venue.active:
            logging.warn("order attempt to inactive venue: %s", venue.key.id())
            errors.append(u"Эта кофейня сейчас недоступна")
            return False
        if delivery_time and not venue.is_open(minutes_offset=delivery_time):
            errors.append(u"Эта кофейня сейчас закрыта")
            return False
    return True


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


def _apply_city_happy_hours_promo(item_dicts, promos_info, venue, delivery_time):
    if venue.key.id() in config.CITY_HAPPY_HOURS:
        schedule = config.CITY_HAPPY_HOURS[venue.key.id()]
        delivery_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=delivery_time)
        if working_hours.check(schedule['days'], schedule['hours'], delivery_time):
            promos_info.append(_CITY_HAPPY_HOURS_PROMO)
            for item_dict in item_dicts:
                if item_dict['item'].price == 150:
                    logging.info(item_dict)
                    item_dict['promos'].append(_CITY_HAPPY_HOURS_PROMO['id'])
                    item_dict['price'] -= 50


def _unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def _group_item_dicts_detailed(item_dicts):
    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'id': None}
        if item_dict['item'].key.id() == possible_group['id'] \
                and item_dict['price'] == possible_group['price'] \
                and item_dict['promos'] == possible_group['promos'] \
                and item_dict['errors'] == possible_group['errors']:
            possible_group['quantity'] += 1
        else:
            result.append({
                'id': item_dict['item'].key.id(),
                'price': item_dict['price'],
                'promos': item_dict['promos'],
                'errors': item_dict['errors'],
                'quantity': 1
            })
    return result


def _group_item_dicts(item_dicts):
    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'id': None}
        if item_dict['item'].key.id() == possible_group['id']:
            possible_group['quantity'] += 1
            possible_group['promos'].append(item_dicts['promos'])
            possible_group['errors'].append(item_dicts['errors'])
        else:
            result.append({
                'id': item_dict['item'].key.id(),
                'promos': item_dict['promos'],
                'errors': item_dict['errors'],
                'quantity': 1
            })
    for dct in result:
        dct['promos'] = _unique(dct['promos'])
        dct['errors'] = _unique(dct['errors'])
    return result


def validate_order(client, items, payment_info, venue, delivery_time, with_details=False):
    item_dicts = []
    for item in items:
        menu_item = MenuItem.get_by_id(int(item["id"]))
        for i in xrange(item["quantity"]):
            item_dicts.append({
                'item': menu_item,
                'price': menu_item.price,
                'errors': [],
                'promos': []
            })

    errors = []
    valid = True
    promos_info = []

    valid = valid and _check_venue(venue, delivery_time, errors)

    if venue and delivery_time:
        _apply_city_happy_hours_promo(item_dicts, promos_info, venue, delivery_time)
    if payment_info:
        _apply_master_promo(item_dicts, promos_info, client, payment_info)

    total_sum = 0
    for item_dict in item_dicts:
        total_sum += item_dict['price']

    grouped_item_dicts = _group_item_dicts(item_dicts)

    result = {
        'valid': valid,
        'errors': errors,
        'items': grouped_item_dicts,
        'promos': promos_info,
        'total_sum': total_sum
    }

    if with_details:
        result['details'] = _group_item_dicts_detailed(item_dicts)

    return result
