# coding=utf-8
import copy
from datetime import datetime, timedelta
import logging
from config import config, VENUE, BAR, Config
from methods import empatika_wallet, empatika_promos
from methods.address_validation import check_address
from methods.rendering import STR_TIME_FORMAT
from methods.working_hours import get_valid_time_str, is_valid_weekday
from models import MenuItem, SingleModifier, GroupModifier, \
    GiftMenuItem, STATUS_AVAILABLE, DeliverySlot, PromoOutcome, MINUTE_SECONDS, \
    HOUR_SECONDS, DAY_SECONDS
from models.order import OrderPositionDetails, GiftPositionDetails, ChosenGroupModifierDetails
from models.venue import DELIVERY, DELIVERY_MAP
from promos import apply_promos


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


def _get_now(delivery_slot, venue, only_day=False):
    now = datetime.utcnow()
    if venue and not (delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS):
        now += timedelta(hours=venue.timezone_offset)
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


def _nice_join(strs):
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]
    return u"%s и %s" % (", ".join(strs[:-1]), strs[-1])


def _check_delivery_type(venue, delivery_type, delivery_time, delivery_slot, delivery_zone, total_sum, errors):
    description = None
    for delivery in venue.delivery_types:
        if delivery.status == STATUS_AVAILABLE and delivery.delivery_type == delivery_type:
            if delivery_zone and delivery_zone.min_sum > total_sum:
                description = u'Минимальная сумма заказа %s' % delivery_zone.min_sum
                errors.append(description)
            if delivery_time < _get_now(delivery_slot, venue) + timedelta(seconds=delivery.min_time-MAX_SECONDS_LOSS):
                description = u'Выберите время больше текущего'
                if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS:
                    description += u' дня'
                else:
                    description += u' времени'
                description += _parse_time(delivery.min_time)
                errors.append(description)
            if delivery_time > _get_now(delivery_slot, venue, only_day=True) + timedelta(seconds=delivery.max_time):
                description = u'Невозможно выбрать время больше текущего дня%s' % _parse_time(delivery.max_time)
                errors.append(description)
            if description:
                return False
            else:
                return True
    errors.append(u'Данный тип доставки недоступен')
    return False


def _check_payment(payment_info, errors):
    if not payment_info:
        errors.append(u'Не выбран тип оплаты')
        return False
    else:
        return True


def _check_address(delivery_type, address, errors):
    if delivery_type == DELIVERY:
        success, description = check_address(address)
        if not success:
            errors.append(description)
        return success
    else:
        return True


def _check_modifier_consistency(item_dicts, gift_dicts, order_gift_dicts, errors):
    def check(item_dicts):
        description = None
        for item_dict in item_dicts:
            item = item_dict['item']
            for single_modifier in item.chosen_single_modifiers:
                if single_modifier.key not in item.single_modifiers:
                    description = u'%s нет для %s' % (single_modifier.title, item.title)
                    errors.append(description)
                    item_dict['errors'].append(description)
            for group_modifier in item.chosen_group_modifiers:
                if group_modifier.key not in item.group_modifiers:
                    description = u'%s нет для %s' % (group_modifier.title, item.title)
                    errors.append(description)
                    item_dict['errors'].append(description)
                choice_confirmed = False
                for choice in group_modifier.choices:
                    if choice.title == group_modifier.choice.title:
                        choice_confirmed = True
                if not choice_confirmed:
                    description = u'%s нет для %s' % (group_modifier.choice.title, group_modifier.title)
                    errors.append(description)
                    item_dict['errors'].append(description)
        return description

    items_description = check(item_dicts)
    gifts_description = check(gift_dicts)
    order_gifts_description = check(order_gift_dicts)
    if items_description or gifts_description or order_gifts_description:
        return False
    else:
        return True


def _check_venue(venue, delivery_time, errors):
    if venue:
        if not venue.active:
            logging.warn("order attempt to inactive venue: %s", venue.key.id())
            if config.PLACE_TYPE == VENUE:
                errors.append(u"Кофейня сейчас недоступна")
            elif config.PLACE_TYPE == BAR:
                errors.append(u"Бар сейчас недоступен")
            else:
                errors.append(u'Заведение сейчас недоступно')
            return False
        if delivery_time:
            if not venue.is_open_by_delivery_time(delivery_time):
                valid, error = is_valid_weekday(venue.working_days, venue.working_hours, delivery_time)
                if not valid:
                    errors.append(error)
                else:
                    errors.append(get_valid_time_str(venue.working_days, venue.working_hours, delivery_time))
                return False
        if venue.problem:
            place_name = config.get_place_str()
            errors.append(u"%s временно не принимает заказы: %s" % (place_name, venue.problem))
            return False
    return True


def _check_restrictions(venue, item_dicts, gift_dicts, order_gift_dicts, delivery_type, errors):
    def check(item_dicts):
        description = None
        delivery_items = []
        delivery_categories = []
        for delivery in venue.delivery_types:
            if delivery.delivery_type == delivery_type:
                delivery_items = delivery.item_restrictions
                delivery_categories = delivery.category_restrictions
        found_categories = []
        for item_dict in item_dicts:
            item = item_dict['item']
            if venue.key in item.restrictions:
                description = u'В "%s" нет %s. Выберите другое заведение.' % (venue.title, item.title)
                errors.append(description)
                item_dict['errors'].append(description)
                substitute = _get_substitute(item, venue)
                if substitute:
                    item_dict['substitutes'].append(substitute)
            if item.key in delivery_items:
                description = u'Невозможно выбрать "%s" для типа "%s"' % (item.title, DELIVERY_MAP[delivery_type])
                errors.append(description)
            category = item.get_category()
            if category and category not in found_categories:
                found_categories.append(category)
        for category in found_categories:
            if category.key in delivery_categories:
                description = u'Невозможно выбрать продукт из категории "%s" для типа "%s"' % (category.title, DELIVERY_MAP[delivery_type])
                errors.append(description)
        return description

    items_description = check(item_dicts)
    gifts_description = check(gift_dicts)
    order_gifts_description = check(order_gift_dicts)
    if items_description or gifts_description or order_gifts_description:
        return False
    else:
        return True


def _check_stop_list(venue, item_dicts, gift_dicts, order_gift_dicts, errors):
    def check(item_dicts):
        description = None
        stop_list_choices = [choice.get().choice_id for choice in venue.group_choice_modifier_stop_list]
        for item_dict in item_dicts:
            item = item_dict['item']
            if item.key in venue.stop_lists:
                description = u'В "%s" позиция "%s" временно недоступна' % (venue.title, item.title)
                errors.append(description)
                item_dict['errors'].append(description)
                substitute = _get_substitute(item, venue)
                if substitute:
                    item_dict['substitutes'].append(substitute)
            for single_modifier in item_dict['single_modifiers']:
                if single_modifier.key in venue.single_modifiers_stop_list:
                    description = u'В "%s" добавка "%s" временно недоступна' % (venue.title, single_modifier.title)
                    errors.append(description)
                    item_dict['errors'].append(description)
            for group_modifier in item_dict['group_modifiers']:
                if group_modifier.choice.choice_id in stop_list_choices or \
                                group_modifier.choice.choice_id in item.stop_list_group_choices:
                    description = u'В "%s" выбор "%s" временно недоступен' % \
                                  (venue.title, group_modifier.choice.title)
                    errors.append(description)
                    item_dict['errors'].append(description)
        return description

    items_description = check(item_dicts)
    gifts_description = check(gift_dicts)
    order_gift_description = check(order_gift_dicts)
    if items_description or gifts_description or order_gift_description:
        return False
    else:
        return True


def _unique(seq):
    if not seq:
        return []
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def _unique_promos(promos):
    if not promos:
        return []
    result = []
    for promo in promos:
        if promo not in result:
            result.append(promo)
    return result


def _group_promos(promos):
    return [promo.validation_dict() for promo in _unique_promos(promos)]


def _is_equal(item_dict1, item_dict2):
    if not item_dict1 or not item_dict2:
        return False
    if item_dict1['item'].key != item_dict2['item'].key:
        return False
    if len(item_dict1['single_modifier_keys']) != len(item_dict2['single_modifier_keys']):
        return False
    for i in xrange(len(item_dict1['single_modifier_keys'])):
        if item_dict1['single_modifier_keys'][i] != item_dict2['single_modifier_keys'][i]:
            return False
    for i in xrange(len(item_dict1['group_modifier_keys'])):
        if item_dict1['group_modifier_keys'][i][0] != item_dict2['group_modifier_keys'][i][0]:
            return False
        if item_dict1['group_modifier_keys'][i][1] != item_dict2['group_modifier_keys'][i][1]:
            return False
    return True


def _group_single_modifiers(modifiers):
    result = {}
    for modifier in modifiers:
        if modifier.id() in result:
            result[modifier.id()]['quantity'] += 1
        else:
            modifier_obj = modifier.get()
            result[modifier.id()] = {
                'id': str(modifier.id()),
                'name': modifier_obj.title,
                'quantity': 1
            }
    return result.values()


def _group_group_modifiers(modifiers):
    result = {}
    for modifier in modifiers:
        key = '%s%s' % (modifier[0].id, modifier[1])
        if key in result:
            result[key]['quantity'] += 1
        else:
            modifier_obj = modifier[0].get()
            choice = modifier_obj.get_choice_by_id(modifier[1])
            result[key] = {
                'id': str(modifier[0].id()),
                'name': choice.title,
                'choice': str(modifier[1]),
                'quantity': 1
            }
    return result.values()


def group_item_dicts(item_dicts):
    def get_group_dict(item_dict):
        return {
            'id': str(item_dict['item'].key.id()),
            'title': item_dict['item'].title,
            'promos': item_dict.get('promos', []),
            'errors': item_dict.get('errors'),
            'substitutes': item_dict.get('substitutes'),
            'image': item_dict.get('image'),
            'quantity': 1,
            'price_without_promos': item_dict['price'],
            'single_modifiers': _group_single_modifiers(item_dict['single_modifier_keys']),
            'group_modifiers': _group_group_modifiers(item_dict['group_modifier_keys']),
            'item_dict': item_dict
        }

    result = []
    for item_dict in item_dicts:
        possible_group = result[-1] if result else {'id': None}
        if _is_equal(item_dict, possible_group.get('item_dict')):
            possible_group['quantity'] += 1
            if item_dict.get('promos'):
                possible_group['promos'].extend(item_dict.get('promos'))
            if item_dict.get('errors'):
                possible_group['errors'].extend(item_dict['errors'])
        else:
            result.append(get_group_dict(item_dict))
    for group in result:
        del group['item_dict']
    for dct in result:
        dct['promos'] = _group_promos(dct.get('promos'))
        dct['errors'] = _unique(dct.get('errors'))
    return result


def set_modifiers(items):
    mod_items = []
    for item in items:
        menu_item = copy.copy(MenuItem.get_by_id(int(item['item_id'])))
        menu_item.chosen_single_modifiers = []
        for single_modifier in item['single_modifiers']:
            single_modifier_obj = copy.copy(SingleModifier.get_by_id(int(single_modifier['single_modifier_id'])))
            for i in xrange(single_modifier['quantity']):
                menu_item.chosen_single_modifiers.append(single_modifier_obj)
        menu_item.chosen_group_modifiers = []
        for group_modifier in item['group_modifiers']:
            group_modifier_obj = copy.copy(GroupModifier.get_by_id(int(group_modifier['group_modifier_id'])))
            group_modifier_obj.choice = group_modifier_obj.get_choice_by_id(int(group_modifier['choice']))
            if group_modifier_obj.choice:
                for i in xrange(group_modifier['quantity']):
                    menu_item.chosen_group_modifiers.append(group_modifier_obj)
        for i in xrange(item['quantity']):
            mod_items.append(menu_item)
    return mod_items


def set_price_with_modifiers(items):
    for item in items:
        price = item.float_price
        for single_modifier in item.chosen_single_modifiers:
            price += single_modifier.float_price
        for group_modifier in item.chosen_group_modifiers:
            price += group_modifier.choice.float_price
        item.total_price = price
    return items


def set_item_dicts(items, is_gift):
    item_dicts = []
    for item in items:
        item_dicts.append({
            'item': item,
            'single_modifiers': item.chosen_single_modifiers,
            'group_modifiers': item.chosen_group_modifiers,
            'single_modifier_keys': [modifier.key for modifier in item.chosen_single_modifiers],
            'group_modifier_keys': [(modifier.key, modifier.choice.choice_id)
                                    for modifier in item.chosen_group_modifiers],
            'price': item.total_price if not is_gift else 0,
            'revenue': item.total_price if not is_gift else 0,
            'errors': [],
            'promos': [],
            'substitutes': []
        })
    return item_dicts


def _check_wallet_payment(total_sum, payment_info):
    return not payment_info or \
           not payment_info.get('wallet_payment') or \
           payment_info['wallet_payment'] <= Config.GET_MAX_WALLET_SUM(total_sum)


def _check_gifts(gifts, client, errors):
    spent_points = 0
    for gift in gifts:
        gift_item = GiftMenuItem.get_by_id(gift.key.id())
        if not gift_item:
            description = u'%s нет в списке подарков' % gift.title
            errors.append(description)
            return False, 0, None
        spent_points += gift_item.points
    if config.PROMOS_API_KEY:
        accum_points = empatika_promos.get_user_points(client.key.id())
    else:
        accum_points = 0
    if accum_points < spent_points:
        description = u'Недостаточно накопленных баллов'
        errors.append(description)
        return False, 0, accum_points
    else:
        return True, accum_points - spent_points, accum_points


def _check_order_gifts(gifts, cancelled_gifts, errors, order=None):
    def get_error():
        description = u'Невозможно добавить %s, как подарок' % gift['item'].title
        errors.append(description)
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
        return False
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
        return True


def get_avail_gifts(points):
    gifts = []
    for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch():
        if gift.points <= points:
            gifts.append(gift)
    return gifts


def validate_order(client, items, gifts, order_gifts, cancelled_order_gifts, payment_info, venue, address,
                   delivery_time, delivery_slot, delivery_type, delivery_zone, with_details=False, order=None):

    items = set_modifiers(items)
    items = set_price_with_modifiers(items)
    item_dicts = set_item_dicts(items, False)

    total_sum_without_promos = 0
    for item in items:
        total_sum_without_promos += item.total_price

    logging.info('total sum without promos = %s' % total_sum_without_promos)

    gifts = set_modifiers(gifts)
    gift_dicts = set_item_dicts(gifts, True)

    logging.info('gift_dicts = %s' % gift_dicts)

    order_gifts = set_modifiers(order_gifts)
    order_gift_dicts = set_item_dicts(order_gifts, True)

    logging.info('order_gift_dicts = %s' % order_gift_dicts)

    cancelled_order_gifts = set_modifiers(cancelled_order_gifts)
    cancelled_order_gift_dicts = set_item_dicts(cancelled_order_gifts, True)

    logging.info('cancelled_order_gift_dicts = %s' % cancelled_order_gift_dicts)

    errors = []
    valid = True
    valid = _check_venue(venue, delivery_time, errors) and valid
    valid = _check_payment(payment_info, errors) and valid
    valid = _check_address(delivery_type, address, errors) and valid
    valid = _check_restrictions(venue, item_dicts, gift_dicts, order_gift_dicts, delivery_type, errors) and valid
    valid = _check_stop_list(venue, item_dicts, gift_dicts, order_gift_dicts, errors) and valid
    valid = _check_delivery_type(venue, delivery_type, delivery_time, delivery_slot, delivery_zone,
                                 total_sum_without_promos, errors) and valid
    valid = _check_modifier_consistency(item_dicts, gift_dicts, order_gift_dicts, errors) and valid
    success, rest_points, full_points = _check_gifts(gifts, client, errors)
    valid = valid and success

    valid = _check_order_gifts(order_gift_dicts, cancelled_order_gift_dicts, errors) and valid

    if not order:
        promo_errors, new_order_gift_dicts, item_dicts, promos_info, total_sum = \
            apply_promos(venue, client, item_dicts, payment_info, delivery_time, delivery_type, order_gift_dicts,
                         cancelled_order_gift_dicts)
        valid = valid and not promo_errors
    else:
        if valid:
            errors, new_order_gift_dicts, item_dicts, promos_info, total_sum = \
                apply_promos(venue, client, item_dicts, payment_info, delivery_time, delivery_type, order_gift_dicts,
                             cancelled_order_gift_dicts, order)
        else:
            new_order_gift_dicts = []
            promos_info = []
            total_sum = 0

    logging.info('item_dicts = %s' % item_dicts)

    if len(item_dicts) or len(gift_dicts):
        grouped_item_dicts = group_item_dicts(item_dicts)
        grouped_gift_dicts = group_item_dicts(gift_dicts)
        grouped_new_order_gift_dicts = group_item_dicts(new_order_gift_dicts)
        grouped_order_gift_dicts = group_item_dicts(order_gift_dicts)
        grouped_cancelled_order_gift_dicts = group_item_dicts(cancelled_order_gift_dicts)
    else:
        grouped_item_dicts = []
        grouped_gift_dicts = []
        grouped_new_order_gift_dicts = []
        grouped_order_gift_dicts = []
        grouped_cancelled_order_gift_dicts = []

    max_wallet_payment = 0.0
    if config.WALLET_ENABLED:
        valid = _check_wallet_payment(total_sum, payment_info) and valid
        wallet_balance = empatika_wallet.get_balance(client.key.id())
        max_wallet_payment = min(Config.GET_MAX_WALLET_SUM(total_sum), wallet_balance / 100.0)
        max_wallet_payment = int(max_wallet_payment * 100) / 100.0

    result = {
        'valid': valid,
        'more_gift': len(get_avail_gifts(rest_points)) > 0,
        'rest_points': rest_points,
        'full_points': full_points,
        'errors': _unique(errors),
        'items': grouped_item_dicts,
        'gifts': grouped_gift_dicts,
        'new_order_gifts': grouped_new_order_gift_dicts,
        'order_gifts': grouped_order_gift_dicts,
        'cancelled_order_gifts': grouped_cancelled_order_gift_dicts,
        'promos': [promo.validation_dict() for promo in _unique_promos(promos_info)],
        'total_sum': total_sum,
        'delivery_sum': None,      # todo: set
        'delivery_sum_str': None,  # todo: set
        'max_wallet_payment': max_wallet_payment,
        'delivery_time': datetime.strftime(delivery_time, STR_TIME_FORMAT)
        if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS
        else datetime.strftime(delivery_time + timedelta(hours=venue.timezone_offset), STR_TIME_FORMAT),
        'delivery_slot_name': delivery_slot.name
        if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS else None
    }
    logging.info('validation result = %s' % result)
    logging.info('total sum = %s' % total_sum)

    if with_details:
        details = []
        for item_dict in item_dicts:
            details_item = OrderPositionDetails(
                item=item_dict['item'].key,
                price=int(item_dict['price'] * 100),  # перевод в копейки
                revenue=item_dict['revenue'],
                promos=[promo.key for promo in item_dict['promos']],
                single_modifiers=[modifier.key for modifier in item_dict['single_modifiers']],
                group_modifiers=[ChosenGroupModifierDetails(group_choice_id=modifier.choice.choice_id,
                                                            group_modifier=modifier.key)
                                 for modifier in item_dict['group_modifiers']]
            )
            details_item.errors = item_dict['errors']
            details.append(details_item)
        result['details'] = details
        details = []
        for item_dict in gift_dicts:
            details_item = GiftPositionDetails(
                gift=GiftMenuItem.get_by_id(item_dict['item'].key.id()).key,
                single_modifiers=[modifier.key for modifier in item_dict['single_modifiers']],
                group_modifiers=[ChosenGroupModifierDetails(group_choice_id=modifier.choice.choice_id,
                                                            group_modifier=modifier.key)
                                 for modifier in item_dict['group_modifiers']]
            )
            details.append(details_item)
        result['gift_details'] = details

    return result


def get_first_error(validation_result):
    if validation_result['errors']:
        return validation_result['errors'][0]
    for item in validation_result['details']:
        if item.errors:
            return item.errors[0]
    return None
