# coding=utf-8
from models.menu import GroupModifier, GroupModifierChoice
from models.order import CashBack, GiftPointsDetails
from models.venue import DELIVERY


def get_item_dict(item_details):
    item = item_details.item.get()
    chosen_group_modifiers = []
    for choice_id in item_details.group_choice_ids:
        modifier = GroupModifier.get_modifier_by_choice(choice_id)
        modifier.choice = modifier.get_choice_by_id(choice_id)
        chosen_group_modifiers.append(modifier)
    for modifier_key in item.group_modifiers:
        if modifier_key not in [modifier.key for modifier in chosen_group_modifiers]:
            modifier = modifier_key.get()
            modifier.choice = GroupModifierChoice(choice_id=None)
            chosen_group_modifiers.append(modifier)
    return {
        'item': item,
        'image': item.picture,
        'single_modifier_keys': sorted(item_details.single_modifiers, key=lambda modifier_key: modifier_key.id()),
        'group_modifier_keys': [(modifier.key, modifier.choice.choice_id)
                                for modifier in sorted(chosen_group_modifiers, key=lambda modifier: modifier.key.id())],
    }


def _get_promo_item_dicts(item_details, item_dicts):
    from methods.orders.validation.validation import is_equal
    if not item_details.item:
        return []
    promo_item_dict = get_item_dict(item_details)
    result_item_dicts = []
    for item_dict in item_dicts:
        if is_equal(promo_item_dict, item_dict, consider_single_modifiers=False):
            result_item_dicts.append(item_dict)
    return result_item_dicts


def _apply_discounts(item_dict, promo, discount, percent=True):
    discount_sum = item_dict['item'].total_price * discount if percent else discount
    if promo not in item_dict['promos']:
        if item_dict['revenue'] >= discount_sum:
            item_dict['revenue'] -= discount_sum
        else:
            item_dict['revenue'] = 0
        item_dict['promos'].append(promo)
        return True
    return False


def _apply_cash_back(item_dict, promo, cash_back, init_total_sum, wallet_payment_sum, order=None):
    if promo not in item_dict['promos']:
        if order:
            cash_back_amount = cash_back * item_dict['price']
            cash_back_without_wallet = cash_back_amount * (1 - wallet_payment_sum / init_total_sum)
            order.cash_backs.append(CashBack(amount=int(cash_back_without_wallet * 100)))
        item_dict['promos'].append(promo)
        return True
    return False


def _apply_total_cash_back(sum_without_wallet, cash_back, order=None):
    if order:
        order.cash_backs.append(CashBack(amount=int(cash_back * sum_without_wallet * 100)))
    return True


def _add_order_gift(item_dict, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts):
    from methods.orders.validation.validation import is_equal
    found = False
    for order_gift_dict in order_gift_dicts:
        if not order_gift_dict.get('found') and is_equal(item_dict, order_gift_dict):
            found = True
            order_gift_dict['found'] = True
            break
    if not found:
        for order_gift_dict in cancelled_order_gift_dicts:
            if not order_gift_dict.get('found') and is_equal(item_dict, order_gift_dict):
                found = True
                order_gift_dict['found'] = True
                break
    if not found:
        new_order_gift_dicts.append(item_dict)


def set_discounts(response, outcome, item_dicts, promo):
    discount = float(outcome.value) / 100.0
    promo_applied = False
    if outcome.item_details.item:
        item_dicts = _get_promo_item_dicts(outcome.item_details, item_dicts)
    for item_dict in item_dicts:
        if _apply_discounts(item_dict, promo, discount):
            promo_applied = True
    response.success = promo_applied
    return response


def set_cash_back(response, outcome, item_dicts, promo, init_total_sum, wallet_payment_sum, order):
    cash_back = float(outcome.value) / 100.0
    promo_applied = False
    if outcome.item_details.item:
        for item_dict in _get_promo_item_dicts(outcome.item_details, item_dicts):
            if _apply_cash_back(item_dict, promo, cash_back, init_total_sum, wallet_payment_sum, order):
                promo_applied = True
    else:
        _apply_total_cash_back(init_total_sum - wallet_payment_sum, cash_back, order)
        promo_applied = True
    if order:
        order.put()
    response.success = promo_applied
    return response


def set_discount_cheapest(response, outcome, item_dicts, promo):
    def get_cheapest(item_dicts):
        if not len(item_dicts):
            return
        cheapest_item_dict = item_dicts[0]
        for item_dict in item_dicts:
            if item_dict['price'] < cheapest_item_dict['price']:
                cheapest_item_dict = item_dict
        return cheapest_item_dict

    discount = float(outcome.value) / 100.0
    promo_applied = False
    item_dict = get_cheapest(item_dicts)
    if item_dict:
        if _apply_discounts(item_dict, promo, discount):
            promo_applied = True
    response.success = promo_applied
    return response


def set_discount_richest(response, outcome, item_dicts, promo):
    def get_richest(item_dicts):
        if not len(item_dicts):
            return
        richest_item_dict = item_dicts[0]
        for item_dict in item_dicts:
            if item_dict['price'] > richest_item_dict['price']:
                richest_item_dict = item_dict
        return richest_item_dict

    discount = float(outcome.value) / 100.0
    promo_applied = False
    item_dict = get_richest(item_dicts)
    if item_dict:
        if _apply_discounts(item_dict, promo, discount):
            promo_applied = True
    response.success = promo_applied
    return response


def set_gift_points(response, outcome, item_dicts, promo, order):
    promo_applied = False
    if outcome.item_details.item:
        for item_dict in _get_promo_item_dicts(outcome.item_details, item_dicts):
            if order:
                order.points_details.append(GiftPointsDetails(item=outcome.item_details.item, points=outcome.value))
                order.put()
            item_dict['promos'].append(promo)
            promo_applied = True
    else:
        if order:
            order.points_details.append(GiftPointsDetails(points=outcome.value * len(item_dicts)))
            order.put()
            for item_dict in item_dicts:
                item_dict['promos'].append(promo)
        promo_applied = True
    response.success = promo_applied
    return response


def set_order_gift_points(response, outcome, order):
    if order:
        order.points_details.append(GiftPointsDetails(points=outcome.value))
        order.put()
    response.success = True
    return response


def add_order_gift(response, outcome, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts):
    _add_order_gift(get_item_dict(outcome.item_details), new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts)
    response.success = True
    return response


def set_fix_discount(response, outcome, promo, item_dicts, init_total_sum):
    if outcome.item_details.item:
        item_dicts = _get_promo_item_dicts(outcome.item_details, item_dicts)
        if item_dicts:
            response.success = True
        for item_dict in item_dicts:
            _apply_discounts(item_dict, promo, outcome.value, percent=False)
    else:
        discount = outcome.value
        if discount > init_total_sum:
            discount = init_total_sum
        response.success = True
        response.discount = discount
    return response


def set_delivery_sum_discount(response, outcome, delivery_type, delivery_zone):
    discount = float(outcome.value) / 100.0
    if delivery_type != DELIVERY or not delivery_zone or not delivery_zone.price:
        return response
    response.success = True
    response.delivery_sum_discount = int(delivery_zone.price * discount)
    return response


def set_delivery_fix_sum_discount(response, outcome, delivery_type, delivery_zone):
    if delivery_type != DELIVERY or not delivery_zone or not delivery_zone.price:
        return response
    response.success = True
    response.delivery_sum_discount = outcome.value
    return response


def set_percent_gift_points(response, outcome, item_dicts, order):
    point_discount = float(outcome.value) / 100.0
    if outcome.item_details.item:
        item_dicts = _get_promo_item_dicts(outcome.item_details, item_dicts)
    points = 0
    for item_dict in item_dicts:
        points += int(point_discount * item_dict['price'])
    if order:
        order.points_details.append(GiftPointsDetails(points=points))
        order.put()
    if points:
        response.success = True
    return response


def set_promo_mark_for_marked_items(response, item_dicts, promo):
    promo_applied = False
    for item_dict in item_dicts:
        if item_dict['temporary_mark']:
            item_dict['persistent_mark'] = True
            item_dict['promos'].append(promo)
            promo_applied = True
    response.success = promo_applied
    return response


def remove_persistent_mark(response, item_dicts, promo):
    promo_applied = False
    for item_dict in item_dicts:
        if item_dict['temporary_mark']:
            item_dict['persistent_mark'] = False
            item_dict['promos'].append(promo)
            promo_applied = True
    response.success = promo_applied
    return response


def add_marked_order_gift(response, item_dicts, new_order_gift_dicts, order_gift_dicts,
                          cancelled_order_gift_dicts):
    promo_applied = False
    for item_dict in item_dicts:
        if item_dict['persistent_mark'] and item_dict['temporary_mark']:
            _add_order_gift(item_dict, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts)
            promo_applied = True
    response.success = promo_applied
    return response


def return_success(response):
    response.success = True
    return response
