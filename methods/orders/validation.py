# coding=utf-8
import logging
import datetime
from config import config

from methods import working_hours
from models import MenuItem, CARD_PAYMENT_TYPE, OrderPositionDetails, Venue


PROMO_SUPPORT_NONE = 0
PROMO_SUPPORT_MASTER = 1
PROMO_SUPPORT_FULL = 2


_OMEGA_VENUE_ID = 5093108584808448
_ETAZHI_VENUE_ID = 5547219436437504
_NOEV_VENUE_ID = 5682617542246400
_ALKON_VENUE_ID = 5224026972618752


def get_promo_support(request):
    ua = request.headers['User-Agent']
    if 'DoubleBRedirect' in ua:  # old server: 1.0, 1.0.1
        return PROMO_SUPPORT_NONE
    if '/1.0' in ua or \
            '/1.1' in ua or \
            ('/1.2 ' in ua and 'Android' in ua):
        return PROMO_SUPPORT_MASTER
    return PROMO_SUPPORT_FULL


_MASTER_PROMO = {
    "id": "master",
    "text": u"Скидка 50% на один напиток при первом заказе картой MasterCard"
}

_CITY_HAPPY_HOURS_PROMO = {
    "id": "city_hh",
    "text": u"Счастливые часы: скидка 50р"
}

_OMEGA_PROMO = {
    "id": "omega",
    "text": u"Скидки в Омега Плаза"
}

_ETAZHI_PROMO = {
    "id": "etazhi",
    "text": u"Скидки в лофт-проекте Этажи"
}

_NOEV_PROMO = {
    "id": "noev",
    "text": u"Скидки в БЦ Ноев Ковчег"
}

_ALKON_PROMO = {
    "id": "alkon",
    "text": u"Скидки в БЦ Алкон"
}


def _nice_join(strs):
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]
    return u"%s и %s" % (", ".join(strs[:-1]), strs[-1])


def _apply_new_menu(item_dicts, venue, supports_new_menu, promos_info):
    prices = {}
    for item_dict in item_dicts:
        item = item_dict['item']
        prices[item.key.id()] = (item.price, item.price_for_old_version)

    if venue:
        if venue.key.id() in config.OLD_MENU_VENUES:
            for item_dict in item_dicts:
                item = item_dict['item']
                original_price, show_price = prices[item.key.id()]
                if original_price != show_price:
                    item_dict['item'] = MenuItem(id=item.key.id(), **item.to_dict())
                    item_dict['item'].price = show_price  # for proper happy hours and other promos

                    item_dict['price'] = item_dict['revenue'] = show_price
                    if supports_new_menu:
                        item_dict['promos'].append("old_menu")

            if supports_new_menu:
                promos_info.append({
                    "id": "old_menu",
                    "text": u"В кофейне %s действует старое меню" % venue.title
                })

        else:
            if not supports_new_menu:
                for item_dict in item_dicts:
                    item = item_dict['item']
                    original_price, show_price = prices[item.key.id()]
                    if original_price != show_price:
                        item_dict['promos'].append("new_menu")

                promos_info.append({
                    "id": "new_menu",
                    "text": u"Новое меню в Даблби"
                })


def _check_venue(venue, delivery_time, errors):
    if venue:
        if not venue.active:
            logging.warn("order attempt to inactive venue: %s", venue.key.id())
            errors.append(u"Эта кофейня сейчас недоступна")
            return False
        if not venue.is_open(minutes_offset=delivery_time):
            errors.append(u"Эта кофейня сейчас закрыта")
            return False
        if venue.problem:
            errors.append(u"Кофейня временно не принимает заказы: %s" % venue.problem)
            return False
    return True


def _check_stop_lists(item_dicts, venue, errors):
    titles = []
    special_msgs = []
    if config.DEBUG:
        # test server: big cappuccino, latte, double espresso not available
        for item_dict in item_dicts:
            if item_dict['item'].key.id() in (1, 2, 5):
                item_dict['errors'].append(u"Тест стоп-листов " * 10)
                item_dict['errors'].append(u"Тест стоп-листов " * 9)
                titles.append(item_dict['item'].title)

    if venue:
        ids = config.STOP_LISTS.get(venue.key.id(), []) + [37]  # TODO hack for new menu
        for item_dict in item_dicts:
            if item_dict['item'].key.id() in ids:
                item_dict['errors'].append(u"Напиток недоступен в этой кофейне")
                titles.append(item_dict['item'].title)

    if venue:
        for item_dict in item_dicts:
            item_id = item_dict['item'].key.id()
            special_venue_ids = config.SPECIALS.get(item_id)
            if special_venue_ids and venue.key.id() not in special_venue_ids:
                special_venue_titles = [Venue.get_by_id(id_).title for id_ in special_venue_ids]
                if len(special_venue_titles) == 1:
                    venue_msg = u"кофейне %s" % special_venue_titles[0]
                else:
                    venue_msg = u"кофейнях: %s" % _nice_join(special_venue_titles)
                error_msg = u"%s можно заказать только в %s" % (item_dict['item'].title, venue_msg)
                special_msgs.append(error_msg)
                item_dict['errors'].append(error_msg)

    # TODO temporary stop lists

    titles = _unique(titles)
    if titles:
        titles_msg = _nice_join(titles)
        stop_list_msg = u"%s сейчас нельзя заказать в этой кофейне" % titles_msg
        errors.append(stop_list_msg)
        return False
    special_msgs = _unique(special_msgs)
    if special_msgs:
        errors.extend(special_msgs)
        return False
    return True


def _apply_master_promo(item_dicts, promos_info, client, payment_info):
    if payment_info["type_id"] == CARD_PAYMENT_TYPE and \
            payment_info["mastercard"] and not client.has_mastercard_orders:
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
                    item_dict['promos'].append(_CITY_HAPPY_HOURS_PROMO['id'])
                    item_dict['price'] -= 50
                    item_dict['revenue'] -= 50
                elif item_dict['item'].price == 200 and item_dict['item'].key.id() == 10:  # cappucino in new menu
                    item_dict['promos'].append(_CITY_HAPPY_HOURS_PROMO['id'])
                    discount = 100
                    if venue.key.id() in config.CAPPUCCINO_150:
                        discount = 50
                    item_dict['price'] -= discount
                    item_dict['revenue'] -= discount


def _apply_venue_discounts(item_dicts, promos_info, venue):
    if venue.key.id() == _OMEGA_VENUE_ID:
        promos_info.append(_OMEGA_PROMO)
        for item_dict in item_dicts:
            if item_dict['item'].price == 250 or item_dict['item'].key.id() in (10, 17):
                item_dict['promos'].append(_OMEGA_PROMO['id'])
                item_dict['price'] -= 50
                item_dict['revenue'] -= 50
    elif venue.key.id() == _ETAZHI_VENUE_ID:
        promos_info.append(_ETAZHI_PROMO)
        for item_dict in item_dicts:
            if item_dict['item'].price in (150, 250):
                item_dict['promos'].append(_ETAZHI_PROMO['id'])
                item_dict['price'] -= 50
                item_dict['revenue'] -= 50
    elif venue.key.id() == _NOEV_VENUE_ID:
        promos_info.append(_NOEV_PROMO)
        for item_dict in item_dicts:
            if item_dict['item'].price == 350 or item_dict['item'].key.id() == 10:
                item_dict['promos'].append(_NOEV_PROMO['id'])
                item_dict['price'] -= 50
                item_dict['revenue'] -= 50
    elif venue.key.id() == _ALKON_VENUE_ID:
        promos_info.append(_ALKON_PROMO)
        for item_dict in item_dicts:
            if item_dict['item'].key.id() in (10, 15, 17, 27, 29):  # cappuccino and old drinks for 300
                item_dict['promos'].append(_ALKON_PROMO['id'])
                item_dict['price'] -= 50
                item_dict['revenue'] -= 50


def _unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def _group_item_dicts(item_dicts):
    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'id': None}
        if item_dict['item'].key.id() == possible_group['id']:
            possible_group['quantity'] += 1
            possible_group['promos'].extend(item_dict['promos'])
            possible_group['errors'].extend(item_dict['errors'])
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


def validate_order(client, items, payment_info, venue, delivery_time, support_level=PROMO_SUPPORT_FULL,
                   supports_new_menu=True, with_details=False):
    item_dicts = []
    for item in items:
        item_id = item.get("id") or item["item_id"]
        menu_item = MenuItem.get_by_id(int(item_id))
        for i in xrange(item["quantity"]):
            item_dicts.append({
                'item': menu_item,
                'price': menu_item.price,
                'revenue': menu_item.price,
                'errors': [],
                'promos': []
            })

    errors = []
    valid = True
    promos_info = []

    valid = _check_venue(venue, delivery_time, errors) and valid

    valid = _check_stop_lists(item_dicts, venue, errors) and valid

    _apply_new_menu(item_dicts, venue, supports_new_menu, promos_info)

    if support_level == PROMO_SUPPORT_FULL:
        if venue:
            _apply_city_happy_hours_promo(item_dicts, promos_info, venue, delivery_time)
            _apply_venue_discounts(item_dicts, promos_info, venue)

    if support_level in (PROMO_SUPPORT_MASTER, PROMO_SUPPORT_FULL):
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
    logging.info(result)

    if with_details:
        details = []
        for item_dict in item_dicts:
            details_item = OrderPositionDetails(
                item=item_dict['item'].key,
                price=item_dict['price'],
                revenue=item_dict['revenue'],
                promos=item_dict['promos']
            )
            details_item.errors = item_dict['errors']
            details.append(details_item)
        result['details'] = details

    return result


def get_first_error(validation_result):
    if validation_result['errors']:
        return validation_result['errors'][0]
    for item in validation_result['details']:
        if item.errors:
            return item.errors[0]
    return None
