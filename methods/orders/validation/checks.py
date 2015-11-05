# coding=utf-8
from datetime import timedelta, datetime
import logging
from google.appengine.api.namespace_manager import namespace_manager
from methods.rendering import latinize

from models.config.config import config, VENUE, BAR
from methods import empatika_promos
from methods.geocoder import get_houses_by_address, get_streets_by_address
from methods.subscription import get_subscription, get_amount_of_subscription_items
from methods.working_hours import check_with_errors, check_in_with_errors, check_restriction, check_today_error
from models import STATUS_AVAILABLE, DeliverySlot, DAY_SECONDS, HOUR_SECONDS, MINUTE_SECONDS, MenuItem
from models.venue import DELIVERY, DELIVERY_MAP, DELIVERY_WHAT_MAP
from models.promo_code import PromoCodePerforming, KIND_ALL_TIME_HACK

__author__ = 'dvpermyakov'

MAX_SECONDS_LOSS = 120


def _get_substitute(origin_item, delivery_type, venue):
    for item in MenuItem.query(MenuItem.title == origin_item.title).fetch():
        if origin_item.key == item.key:
            continue
        if venue.key not in item.restrictions:
            if item.price != origin_item.price:
                if delivery_type == DELIVERY:
                    place = u'при заказе на доставку'
                else:
                    place = u'в выбранной точке %s' % venue.title
                description = u'Позиция "%s" имеет другую цену %s. ' \
                              u'Заменить?' % (item.title, place)
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
            if delivery.today_schedule and datetime.now().day == delivery_time.day:
                valid, error = check_today_error(delivery.today_schedule,
                                                 datetime.now() + timedelta(hours=venue.timezone_offset))
                if not valid:
                    return False, error
            valid, error = check_restriction(delivery.schedule_restriction,
                                             delivery_time + timedelta(hours=venue.timezone_offset),
                                             DELIVERY_WHAT_MAP[delivery.delivery_type])
            if not valid:
                return False, error
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


def check_payment(venue, payment_info, item_dicts, gift_dicts, shared_gifts):
    if not payment_info:
        if item_dicts or not (gift_dicts and shared_gifts):
            return False, u'Не выбран тип оплаты'
    for payment_key in venue.payment_restrictions:
        if str(payment_key.id()) == str(payment_info.get('type_id')):
            return False, u'Данный тип оплаты не доступен в этой кофейне'
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


def check_venue(venue, delivery_time, delivery_type, client):
    for performing in PromoCodePerforming.query(PromoCodePerforming.client == client.key,
                                                PromoCodePerforming.status == PromoCodePerforming.PROCESSING_ACTION).fetch():
        if performing.promo_code.get().kind == KIND_ALL_TIME_HACK:
            return True, None
    if not delivery_time:
        return False, u'Не выбрано время'
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
            valid, error = check_with_errors(venue.schedule, delivery_time + timedelta(hours=venue.timezone_offset))
            if not valid:
                return False, error
        if venue.problem:
            place_name = config.get_place_str()
            return False, u"%s временно не принимает заказы: %s" % (place_name, venue.problem)
        if venue.time_break:
            for time_break in venue.time_break:
                valid, error = check_in_with_errors(time_break, delivery_time + timedelta(hours=venue.timezone_offset))
                if not valid:
                    return False, error
    else:
        if delivery_type == DELIVERY:
            return False, u'На Ваш адрес доставки нет. Подробности в настройках о компании.'
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
        for item_dict in item_dicts:
            item = item_dict['item']
            if venue.key in item.restrictions:
                if delivery_type == DELIVERY:
                    description = u'При заказе на доставку нет %s.' % item.title
                else:
                    description = u'В "%s" нет %s. Выберите другое заведение.' % (venue.title, item.title)
                item_dict['errors'].append(description)
                substitute = _get_substitute(item, delivery_type, venue)
                if substitute:
                    item_dict['substitutes'].append(substitute)
                    if item_dict.get('gift_obj'):
                        del item_dict['substitutes']
                        description = None
            if item.key in delivery_items:
                description = u'Невозможно выбрать "%s" для типа "%s"' % (item.title, DELIVERY_MAP[delivery_type])
            if item.category in delivery_categories:
                description = u'Невозможно выбрать продукт из категории "%s" для типа "%s"' % (item.category.get().title, DELIVERY_MAP[delivery_type])
        return description

    items_description = check(item_dicts)
    if items_description:
        return False, items_description
    gifts_description = check(gift_dicts)
    if gifts_description:
        return False, gifts_description
    order_gifts_description = check(order_gift_dicts)
    if order_gifts_description:
        if namespace_manager.get_namespace() == 'sushimarket':
            return True, None
        else:
            return False, order_gifts_description
    else:
        return True, None


def check_stop_list(venue, delivery_type, item_dicts, gift_dicts, order_gift_dicts):
    def check(item_dicts):
        description = None
        stop_list_choices = [choice.get().choice_id for choice in venue.group_choice_modifier_stop_list]
        for item_dict in item_dicts:
            item = item_dict['item']
            if item.key in venue.stop_lists:
                description = u'В "%s" позиция "%s" временно недоступна' % (venue.title, item.title)
                item_dict['errors'].append(description)
                substitute = _get_substitute(item, delivery_type, venue)
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


def check_wallet_payment(total_sum, wallet_payment_sum, venue):
    valid = not config.WALLET_ENABLED or wallet_payment_sum <= config.GET_MAX_WALLET_SUM(total_sum)
    if not valid:
        return False, u'Невозможно оплатить бонусами сумму большую, чем %s' % config.GET_MAX_WALLET_SUM(total_sum)
    if wallet_payment_sum and venue.wallet_restriction:
        return False, u'В данном заведение невозможна оплата баллами'
    return True, None


def check_gifts(gifts, client):
    spent_points = 0
    for gift in gifts:
        gift_item = gift.gift_obj
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


def check_address(delivery_type, address):
    if delivery_type == DELIVERY:
        address = address.get('address') if address else None
        if not address:
            return False, u'Введите адрес'
        if not address['city'] and not address['street']:
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


def check_client_info(client, delivery_type, order):
    if config.COMPULSORY_DELIVERY_EMAIL_VALIDATES:
        if delivery_type == DELIVERY and not client.email and order:
            return False, u'Не введен email'
    if config.CLIENT_MODULE and config.CLIENT_MODULE.status == STATUS_AVAILABLE:
        for field in config.CLIENT_MODULE.extra_fields:
            if not field.required:
                continue
            if not client.extra_data or not client.extra_data.get(latinize(field.title)):
                return False, u'Не введено поле "%s"' % field.title
    return True, None


def check_subscription(client, item_dicts):
    subscription = get_subscription(client)
    amount = get_amount_of_subscription_items(item_dicts)
    logging.info('Subscription needs %s points' % amount)
    logging.info('Subscription is found = %s' % subscription)
    if amount:
        if not subscription:
            return False, u'У Вас нет абонемента'
        if subscription.rest < amount:
            return False, u'Не хватает позиций на абонементе'
    return True, None


def check_empty_order(item_dicts, gift_dicts, order_gift_dicts, shared_gift_dicts):
    if not item_dicts and not gift_dicts and not order_gift_dicts and not shared_gift_dicts:
        return False, u'Добавьте что-нибудь в заказ'
    return True, None
