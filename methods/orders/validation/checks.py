# coding=utf-8
from datetime import timedelta, datetime
import logging
from config import config, VENUE, BAR
from methods import empatika_promos
from methods.map import get_houses_by_address, get_streets_by_address
from methods.working_hours import is_valid_weekday, get_valid_time_str
from models import STATUS_AVAILABLE, DeliverySlot, DAY_SECONDS, HOUR_SECONDS, MINUTE_SECONDS, PromoOutcome, GiftMenuItem, MenuItem, MenuCategory
from models.order import OrderPositionDetails
from models.venue import DELIVERY, DELIVERY_MAP

__author__ = 'dvpermyakov'

MAX_SECONDS_LOSS = 120


def _get_substitute(origin_item, venue):
    for item in MenuItem.query(MenuItem.title == origin_item.title).fetch():
        if origin_item.key == item.key:
            continue
        if venue.key not in item.restrictions:
            if item.price != origin_item.price:
                description = u'Позиция "%s" имеет другую цену в выбранной точке %s. ' \
                              u'Заменить?' % (item.title, venue.title)
                auto = False
            else:
                description = u'Позиция должна автоматически замениться'
                auto = True
            return {
                'item_id': str(item.key.id()),
                'description': description,
                'auto_replace': auto
            }


def _get_now(delivery_slot, only_day=False):
    now = datetime.utcnow()
    if (delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS) or only_day:
        now = now.replace(hour=0, minute=0, second=0)
    return now


def _parse_time(time):
    def parse(time):
        if time / 10 == 0:
            time = '0%s' % time
        return time

    days = time / DAY_SECONDS
    time %= DAY_SECONDS
    hours = parse(time / HOUR_SECONDS)
    time %= HOUR_SECONDS
    minutes = parse(time / MINUTE_SECONDS)

    description = u''
    if days or minutes != '00' or hours != '00':
        description += u' на'
    if days:
        description += u' %s дн.' % days
    if minutes != '00' or hours != '00':
        description += u' %sч:%sм' % (hours, minutes)
    return description


def check_delivery_type(venue, delivery_type, delivery_time, delivery_slot, delivery_zone, total_sum):
    description = None
    for delivery in venue.delivery_types:
        if delivery.status == STATUS_AVAILABLE and delivery.delivery_type == delivery_type:
            if delivery_zone and delivery_zone.min_sum > total_sum:
                description = u'Минимальная сумма заказа %s' % delivery_zone.min_sum
            if delivery_time < _get_now(delivery_slot) + timedelta(seconds=delivery.min_time-MAX_SECONDS_LOSS):
                description = u'Выберите время больше текущего'
                if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS:
                    description += u' дня'
                else:
                    description += u' времени'
                description += _parse_time(delivery.min_time)
            if delivery_time > _get_now(delivery_slot, only_day=True) + timedelta(seconds=delivery.max_time):
                description = u'Невозможно выбрать время больше текущего дня%s' % _parse_time(delivery.max_time)
            if description:
                return False, description
            else:
                return True, None
    return False, u'Данный тип доставки недоступен'


def check_delivery_time(delivery_time):
    if not delivery_time:
        return False, u'Не выбрано время'
    else:
        return True, None


def check_payment(payment_info):
    if not payment_info:
        return False, u'Не выбран тип оплаты'
    else:
        return True, None


def check_modifier_consistency(item_dicts, gift_dicts, order_gift_dicts):
    def check(item_dicts):
        description = None
        for item_dict in item_dicts:
            item = item_dict['item']
            for single_modifier in item.chosen_single_modifiers:
                if single_modifier.key not in item.single_modifiers:
                    description = u'%s нет для %s' % (single_modifier.title, item.title)
                    item_dict['errors'].append(description)
            for group_modifier in item.chosen_group_modifiers:
                if group_modifier.key not in item.group_modifiers:
                    description = u'%s нет для %s' % (group_modifier.title, item.title)
                    item_dict['errors'].append(description)
                choice_confirmed = False
                for choice in group_modifier.choices:
                    if choice.title == group_modifier.choice.title:
                        choice_confirmed = True
                if not choice_confirmed:
                    description = u'%s нет для %s' % (group_modifier.choice.title, group_modifier.title)
                    item_dict['errors'].append(description)
        return description

    items_description = check(item_dicts)
    if items_description:
        return False, items_description
    gifts_description = check(gift_dicts)
    if gifts_description:
        return False, gifts_description
    order_gifts_description = check(order_gift_dicts)
    if order_gifts_description:
        return False, order_gifts_description
    return True, None


def check_venue(venue, delivery_time):
    if venue:
        if not venue.active:
            logging.warn("order attempt to inactive venue: %s", venue.key.id())
            if config.PLACE_TYPE == VENUE:
                error = u"Кофейня сейчас недоступна"
            elif config.PLACE_TYPE == BAR:
                error = u"Бар сейчас недоступен"
            else:
                error = u'Заведение сейчас недоступно'
            return False, error
        if delivery_time:
            if not venue.is_open_by_delivery_time(delivery_time):
                valid, error = is_valid_weekday(venue.working_days, venue.working_hours, delivery_time)
                if valid:
                    return False, get_valid_time_str(venue.working_days, venue.working_hours, delivery_time)
                else:
                    return False, u'В этот день недели заказы не принимаются'
        if venue.problem:
            place_name = config.get_place_str()
            return False, u"%s временно не принимает заказы: %s" % (place_name, venue.problem)
    else:
        return False, u'Не выбрано заведение'
    return True, None


def check_restrictions(venue, item_dicts, gift_dicts, order_gift_dicts, delivery_type):
    def check(item_dicts):
        description = None
        delivery_items = []
        delivery_categories = []
        for delivery in venue.delivery_types:
            if delivery.delivery_type == delivery_type:
                delivery_items = delivery.item_restrictions
                delivery_categories = delivery.category_restrictions
        items = []
        for item_dict in item_dicts:
            item = item_dict['item']
            if venue.key in item.restrictions:
                description = u'В "%s" нет %s. Выберите другое заведение.' % (venue.title, item.title)
                item_dict['errors'].append(description)
                substitute = _get_substitute(item, venue)
                if substitute:
                    item_dict['substitutes'].append(substitute)
            if item.key in delivery_items:
                description = u'Невозможно выбрать "%s" для типа "%s"' % (item.title, DELIVERY_MAP[delivery_type])
            if item not in items:
                items.append(item)
        if delivery_categories:
            for item in items:
                for category in MenuCategory.query().fetch():
                    if item.key in category.menu_items and category.key in delivery_categories:
                        description = u'Невозможно выбрать продукт из категории "%s" для типа "%s"' % (category.title, DELIVERY_MAP[delivery_type])
        return description

    items_description = check(item_dicts)
    if items_description:
        return False, items_description
    gifts_description = check(gift_dicts)
    if gifts_description:
        return False, gifts_description
    order_gifts_description = check(order_gift_dicts)
    if order_gifts_description:
        return False, order_gift_dicts
    else:
        return True, None


def check_stop_list(venue, item_dicts, gift_dicts, order_gift_dicts):
    def check(item_dicts):
        description = None
        stop_list_choices = [choice.get().choice_id for choice in venue.group_choice_modifier_stop_list]
        for item_dict in item_dicts:
            item = item_dict['item']
            if item.key in venue.stop_lists:
                description = u'В "%s" позиция "%s" временно недоступна' % (venue.title, item.title)
                item_dict['errors'].append(description)
                substitute = _get_substitute(item, venue)
                if substitute:
                    item_dict['substitutes'].append(substitute)
            for single_modifier in item_dict['single_modifiers']:
                if single_modifier.key in venue.single_modifiers_stop_list:
                    description = u'В "%s" добавка "%s" временно недоступна' % (venue.title, single_modifier.title)
                    item_dict['errors'].append(description)
            for group_modifier in item_dict['group_modifiers']:
                if group_modifier.choice.choice_id in stop_list_choices or \
                                group_modifier.choice.choice_id in item.stop_list_group_choices:
                    description = u'В "%s" выбор "%s" временно недоступен' % \
                                  (venue.title, group_modifier.choice.title)
                    item_dict['errors'].append(description)
        return description

    items_description = check(item_dicts)
    if items_description:
        return False, items_description
    gifts_description = check(gift_dicts)
    if gifts_description:
        return False, gifts_description
    order_gift_description = check(order_gift_dicts)
    if order_gift_description:
        return False, order_gift_description
    return True, None


def check_wallet_payment(total_sum, payment_info):
    valid = not payment_info.get('wallet_payment') or payment_info['wallet_payment'] <= config.Config.GET_MAX_WALLET_SUM(total_sum)
    if valid:
        return True, None
    else:
        return False, u'Невозможно оплатить бонусами сумму большую, чем %s' % config.Config.GET_MAX_WALLET_SUM(total_sum)


def check_gifts(gifts, client):
    spent_points = 0
    for gift in gifts:
        gift_item = GiftMenuItem.get_by_id(gift.key.id())
        if not gift_item:
            description = u'%s нет в списке подарков' % gift.title
            return False, description, 0, None
        spent_points += gift_item.points
    if config.PROMOS_API_KEY:
        accum_points = empatika_promos.get_user_points(client.key.id())
    else:
        accum_points = 0
    if accum_points < spent_points:
        description = u'Недостаточно накопленных баллов'
        return False, description, 0, accum_points
    else:
        return True, None, accum_points - spent_points, accum_points


def check_order_gifts(gifts, cancelled_gifts, order=None):
    def get_error():
        description = u'Невозможно добавить %s, как подарок' % gift['item'].title
        return description

    description = None
    for gift in gifts:
        if not gift['promos']:
            description = get_error()
        for promo in gift['promos']:
            if PromoOutcome.ORDER_GIFT not in [outcome.method for outcome in promo.outcomes]:
                description = get_error()
    for gift in cancelled_gifts:
        if not gift['promos']:
            description = get_error()
        for promo in gift['promos']:
            if PromoOutcome.ORDER_GIFT not in [outcome.method for outcome in promo.outcomes]:
                description = get_error()
    if description:
        return False, description
    else:
        if order:
            gift_details = []
            for gift in gifts:
                gift_details.append(OrderPositionDetails(
                    item=gift['item'].key,
                    price=0,
                    revenue=0,
                    promos=[promo.key for promo in gift['promos']],
                    single_modifiers=[],  # todo: is it flexible?
                    group_modifiers=[]    # todo: is it flexible?
                ))
            order.order_gift_details = gift_details
            order.put()
        return True, None


def check_address(delivery_type, address):
    if delivery_type == DELIVERY:
        address = address.get('address') if address else None
        if not address:
            return False, u'Введите адрес'
        if not address['city']:
            return False, u'Не выбран город'
        if not address['street']:
            return False, u'Не выбрана улица'
        if config.COMPULSORY_ADDRESS_VALIDATES:
            street_found = False
            candidates = get_streets_by_address(address['city'], address['street'])
            for candidate in candidates:
                if candidate['address']['city'] == address['city']:
                    if candidate['address']['street'] == address['street']:
                        street_found = True
            if not street_found:
                error = u'Введенная улица не найдена'
                if address['home']:
                    if candidates:
                        error += u'. Возможно, Вы имели ввиду улицу "%s"' % candidates[0]['address']['street']
                    return False, error
                else:
                    return False, u'. Возможно, Вы пропустили разграничитель между улицей и домом - запятую'
            else:
                if not address['home']:
                    return False, u'Введите номер дома'
            home_found = False
            candidates = get_houses_by_address(address['city'], address['street'], address['home'])
            for candidate in candidates:
                if candidate['address']['city'] == address['city']:
                    if candidate['address']['street'] == address['street']:
                        if candidate['address']['home'] == address['home']:
                            home_found = True
            if not home_found:
                error = u'Введенный дом не найден'
                if candidates:
                    error += u'. Возможно, Вы имели ввиду дом "%s"' % candidates[0]['address']['home']
                return False, error
        if not address['flat']:
            return False, u'Не выбрана квартира'
    return True, None