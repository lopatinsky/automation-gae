# coding=utf-8
import copy
from datetime import datetime, timedelta
import logging
from config import config
from methods import empatika_wallet
from methods.orders.promos import apply_promos
from methods.rendering import STR_DATETIME_FORMAT
from models import MenuItem, SingleModifier, GroupModifier, \
    GiftMenuItem, STATUS_AVAILABLE, DeliverySlot
from models.order import OrderPositionDetails, GiftPositionDetails, ChosenGroupModifierDetails
from checks import check_delivery_time, check_delivery_type, check_gifts, check_modifier_consistency, \
    check_payment, check_restrictions, check_stop_list, check_venue, check_wallet_payment, check_address
from models.venue import DELIVERY


def _nice_join(strs):
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]
    return u"%s и %s" % (", ".join(strs[:-1]), strs[-1])


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
        if promo.visible and promo not in result:
            result.append(promo)
    return result


def _group_promos(promos):
    return [promo.validation_dict() for promo in _unique_promos(promos)]


def is_equal(item_dict1, item_dict2):
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
        if is_equal(item_dict, possible_group.get('item_dict')):
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


def set_modifiers(items, with_gift_obj):
    mod_items = []
    for item in items:
        menu_item = copy.copy(MenuItem.get_by_id(int(item['item_id'])))
        if with_gift_obj:
            menu_item.gift_obj = item['gift_obj']
        else:
            menu_item.gift_obj = None
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
            'image': item.picture,
            'gift_obj': item.gift_obj if hasattr(item, 'gift_obj') else None,
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


def get_avail_gifts(points):
    gifts = []
    for gift in GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).fetch():
        if gift.points <= points:
            gifts.append(gift)
    return gifts


def _get_response_dict(valid, total_sum, item_dicts, gift_dicts, order_gifts, cancelled_order_gifts, error=None):
    return {
        'valid': valid,
        'more_gift': False,
        'rest_points': 0,
        'full_points': 0,
        'errors': [error] if error else [],
        'items': group_item_dicts(item_dicts) if item_dicts else [],
        'gifts': group_item_dicts(gift_dicts) if gift_dicts else [],
        'new_order_gifts': [],
        'unavail_order_gifts': [],
        'order_gifts': group_item_dicts(order_gifts) if item_dicts else [],
        'cancelled_order_gifts': group_item_dicts(cancelled_order_gifts) if item_dicts else [],
        'promos': [],
        'total_sum': total_sum,
        'delivery_sum': 0,
        'delivery_sum_str': '',
        'max_wallet_payment': 0,
        'delivery_time': '',
        'delivery_slot_name': ''
    }


def validate_order(client, items, gifts, order_gifts, cancelled_order_gifts, payment_info, venue, address,
                   delivery_time, delivery_slot, delivery_type, delivery_zone, with_details=False, order=None):
    def send_error(error):
        logging.warning('Sending error: %s' % error)
        return _get_response_dict(False, total_sum_without_promos, item_dicts, gift_dicts, order_gifts,
                                  cancelled_order_gifts, error)

    items = set_modifiers(items, False)
    items = set_price_with_modifiers(items)
    item_dicts = set_item_dicts(items, False)

    total_sum_without_promos = 0
    for item in items:
        total_sum_without_promos += item.total_price

    logging.info('total sum without promos = %s' % total_sum_without_promos)

    for gift in gifts:
        gift_obj = GiftMenuItem.get_by_id(int(gift['item_id']))
        gift['item_id'] = gift_obj.item.id()
        gift['gift_obj'] = gift_obj
    gifts = set_modifiers(gifts, True)
    gift_dicts = set_item_dicts(gifts, True)

    logging.info('gift_dicts = %s' % gift_dicts)

    order_gifts = set_modifiers(order_gifts, False)
    order_gift_dicts = set_item_dicts(order_gifts, True)

    logging.info('order_gift_dicts = %s' % order_gift_dicts)

    cancelled_order_gifts = set_modifiers(cancelled_order_gifts, False)
    cancelled_order_gift_dicts = set_item_dicts(cancelled_order_gifts, True)

    logging.info('cancelled_order_gift_dicts = %s' % cancelled_order_gift_dicts)
    valid, error = check_address(delivery_type, address)
    if not valid:
        return send_error(error)
    valid, error = check_venue(venue, delivery_time, delivery_type, client)
    if not valid:
        return send_error(error)
    valid, error = check_payment(payment_info)
    if not valid:
        return send_error(error)
    valid, error = check_delivery_time(delivery_time)
    if not valid:
        return send_error(error)
    valid, error = check_delivery_type(venue, delivery_type, delivery_time, delivery_slot, delivery_zone,
                                       total_sum_without_promos)
    if not valid:
        return send_error(error)
    valid, error = check_stop_list(venue, item_dicts, gift_dicts, order_gift_dicts)
    if not valid:
        return send_error(error)
    valid, error = check_modifier_consistency(item_dicts, gift_dicts, order_gift_dicts)
    if not valid:
        return send_error(error)
    valid, error = check_restrictions(venue, item_dicts, gift_dicts, order_gift_dicts, delivery_type)
    if not valid:
        return send_error(error)
    success, error, rest_points, full_points = check_gifts(gifts, client)
    if not valid:
        return send_error(error)

    wallet_payment_sum = payment_info['wallet_payment'] if payment_info.get('wallet_payment') else 0.0
    if config.WALLET_ENABLED:
        valid, error = check_wallet_payment(total_sum_without_promos + (delivery_zone.price if delivery_zone else 0),
                                            wallet_payment_sum)
        if not valid:
            return send_error(error)

    if not order:
        promo_error, new_order_gift_dicts, unavail_order_gift_dicts, item_dicts, promos_info, total_sum, delivery_zone = \
            apply_promos(venue, client, item_dicts, payment_info, wallet_payment_sum, delivery_time, delivery_type,
                         delivery_zone, order_gift_dicts, cancelled_order_gift_dicts)
        if promo_error:
            return send_error(promo_error)
    else:
        error, new_order_gift_dicts, unavail_order_gift_dicts, item_dicts, promos_info, total_sum, delivery_zone = \
            apply_promos(venue, client, item_dicts, payment_info, wallet_payment_sum, delivery_time, delivery_type,
                         delivery_zone, order_gift_dicts, cancelled_order_gift_dicts, order)

    wallet_payment_sum = payment_info['wallet_payment'] if payment_info.get('wallet_payment') else 0.0
    if config.WALLET_ENABLED:
        valid, error = check_wallet_payment(total_sum + (delivery_zone.price if delivery_zone else 0),
                                            wallet_payment_sum)
        if not valid:
            return send_error(error)

    max_wallet_payment = 0.0
    if config.WALLET_ENABLED:
        wallet_balance = empatika_wallet.get_balance(client.key.id())
        max_wallet_payment = min(config.GET_MAX_WALLET_SUM(total_sum + (delivery_zone.price if delivery_zone else 0)),
                                 wallet_balance / 100.0)
        max_wallet_payment = int(max_wallet_payment * 100) / 100.0
        if not item_dicts and not gift_dicts:
            max_wallet_payment = 0.0

    logging.info('item_dicts = %s' % item_dicts)

    if len(item_dicts) or len(gift_dicts):
        grouped_item_dicts = group_item_dicts(item_dicts)
        grouped_gift_dicts = group_item_dicts(gift_dicts)
        grouped_new_order_gift_dicts = group_item_dicts(new_order_gift_dicts)
        grouped_unavail_order_gift_dicts = group_item_dicts(unavail_order_gift_dicts)
        grouped_order_gift_dicts = group_item_dicts(order_gift_dicts)
        grouped_cancelled_order_gift_dicts = group_item_dicts(cancelled_order_gift_dicts)
    else:
        grouped_item_dicts = []
        grouped_gift_dicts = []
        grouped_new_order_gift_dicts = []
        grouped_unavail_order_gift_dicts = []
        grouped_order_gift_dicts = []
        grouped_cancelled_order_gift_dicts = []

    delivery_sum = delivery_zone.price if delivery_zone else 0
    if not item_dicts and not gift_dicts:
        delivery_sum = 0
        delivery_sum_str = u''
    else:
        if delivery_sum:
            delivery_sum_str = u'Стоимость доставки %sр' % delivery_sum
        else:
            if delivery_type == DELIVERY:
                delivery_sum_str = u'Бесплатная доставка'
            else:
                delivery_sum_str = u''
        if config.ADDITION_INFO_ABOUT_DELIVERY:
            delivery_sum_str += u'. %s' % config.ADDITION_INFO_ABOUT_DELIVERY
        if delivery_zone:
            if not delivery_zone.found:
                delivery_sum_str += u'. Точные условия доставки будут уточнены у оператора'
            else:
                if delivery_zone.comment:
                    delivery_sum_str += u'. %s' % delivery_zone.comment
    if delivery_type != DELIVERY:
        delivery_sum_str = u''
    result = {
        'valid': valid,
        'more_gift': len(get_avail_gifts(rest_points)) > 0,
        'rest_points': rest_points,
        'full_points': full_points,
        'errors': [],
        'items': grouped_item_dicts,
        'gifts': grouped_gift_dicts,
        'new_order_gifts': grouped_new_order_gift_dicts,
        'unavail_order_gifts': grouped_unavail_order_gift_dicts,
        'order_gifts': grouped_order_gift_dicts,
        'cancelled_order_gifts': grouped_cancelled_order_gift_dicts,
        'promos': [promo.validation_dict() for promo in _unique_promos(promos_info)],
        'total_sum': total_sum,
        'delivery_sum': delivery_sum,
        'delivery_sum_str': delivery_sum_str,
        'max_wallet_payment': max_wallet_payment,
        'delivery_time': datetime.strftime(delivery_time, STR_DATETIME_FORMAT)
        if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS
        else datetime.strftime(delivery_time + timedelta(hours=venue.timezone_offset), STR_DATETIME_FORMAT),
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
                gift=item_dict['gift_obj'].key,
                single_modifiers=[modifier.key for modifier in item_dict['single_modifiers']],
                group_modifiers=[ChosenGroupModifierDetails(group_choice_id=modifier.choice.choice_id,
                                                            group_modifier=modifier.key)
                                 for modifier in item_dict['group_modifiers']]
            )
            details.append(details_item)
        result['gift_details'] = details
        details = []
        for item_dict in order_gift_dicts:
            details_item = OrderPositionDetails(
                item=item_dict['item'].key,
                price=0,
                revenue=0,
                promos=[promo.key for promo in item_dict['promos']],
                single_modifiers=[modifier.key for modifier in item_dict['single_modifiers']],
                group_modifiers=[ChosenGroupModifierDetails(group_choice_id=modifier.choice.choice_id,
                                                            group_modifier=modifier.key)
                                 for modifier in item_dict['group_modifiers']]
            )
            details.append(details_item)
        result['order_gift_details'] = details
    return result


def get_first_error(validation_result):
    if validation_result['errors']:
        return validation_result['errors'][0]
    for item in validation_result['details']:
        if item.errors:
            return item.errors[0]
    return None
