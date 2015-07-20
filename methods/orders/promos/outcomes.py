# coding=utf-8
from models import MenuItem
from models.order import CashBack, GiftPointsDetails
from models.venue import DELIVERY


def _get_item_keys(item_dicts):
    result = {}
    for item_dict in item_dicts:
        if result.get(item_dict['item'].key):
            result[item_dict['item'].key].append(item_dict)
        else:
            result[item_dict['item'].key] = [item_dict]
    return result


def _check_item(outcome, item_dict):
    if item_dict['item'].key != outcome.item_details.item:
        return False
    item_choice_ids = [modifier_key[1] for modifier_key in item_dict['group_modifier_keys']]
    for choice_id in outcome.item_details.group_choice_ids:
        if choice_id not in item_choice_ids:
            return False
    return True


def _apply_discounts(item_dict, promo, discount):
        if promo not in item_dict['promos']:
            if item_dict['revenue'] >= item_dict['price'] * discount:
                item_dict['revenue'] -= item_dict['price'] * discount
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


def set_discounts(response, outcome, item_dicts, promo):
    discount = float(outcome.value) / 100.0
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item_details.item):
        for item_dict in item_keys[outcome.item_details.item]:
            if _check_item(outcome, item_dict):
                if _apply_discounts(item_dict, promo, discount):
                    promo_applied = True
    if not outcome.item_details.item_required:
        for item_dict in item_dicts:
            if _apply_discounts(item_dict, promo, discount):
                promo_applied = True
    response.success = promo_applied
    return response


def set_cash_back(response, outcome, item_dicts, promo, init_total_sum, wallet_payment_sum, order):
    cash_back = float(outcome.value) / 100.0
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item_details.item):
        for item_dict in item_keys[outcome.item_details.item]:
            if _check_item(outcome, item_dict):
                if _apply_cash_back(item_dict, promo, cash_back, init_total_sum, wallet_payment_sum, order):
                    promo_applied = True
    if not outcome.item_details.item_required:
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
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item_details.item):  # Not implemented, unfortunately
        pass
    if not outcome.item_details.item_required:
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
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item_details.item):  # Not implemented, unfortunately
        pass
    if not outcome.item_details.item_required:
        item_dict = get_richest(item_dicts)
        if item_dict:
            if _apply_discounts(item_dict, promo, discount):
                promo_applied = True
    response.success = promo_applied
    return response


def set_gift_points(response, outcome, item_dicts, promo, order):
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item_details.item):
        for item_dict in item_dicts:
            if _check_item(outcome, item_dict):
                if order:
                    order.points_details.append(GiftPointsDetails(item=outcome.item_details.item, points=outcome.value))
                    order.put()
                item_dict['promos'].append(promo)
                promo_applied = True
    if not outcome.item_details.item_required:
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


def add_order_gift(response, outcome, promo, new_order_gift_dicts, unavail_order_gift_dicts, order_gift_dicts,
                   cancelled_order_gift_dicts):
    from methods.orders.validation.validation import set_item_dicts
    gift = MenuItem.get_by_id(int(outcome.value))
    if not gift:
        response.error = u'Акция подарок по заказу не привязана к продукту'
        response.success = False
        return response
    found = False
    for order_gift_dict in order_gift_dicts:
        if order_gift_dict['item'].key == gift.key and promo not in order_gift_dict['promos']:
            found = True
            order_gift_dict['promos'].append(promo)
            order_gift_dict['found'] = True
            break
    if not found:
        for order_gift_dict in cancelled_order_gift_dicts:
            if order_gift_dict['item'].key == gift.key and promo not in order_gift_dict['promos']:
                found = True
                order_gift_dict['promos'].append(promo)
                order_gift_dict['found'] = True
                break
    if not found:
        gift.chosen_single_modifiers = []  # todo: is it flexible?
        gift.chosen_group_modifiers = []   # todo: is it flexible?
        item_dict = set_item_dicts([gift], True)[0]
        item_dict['promos'].append(promo)
        new_order_gift_dicts.append(item_dict)
    for order_gift_dict in order_gift_dicts[:]:
        if not order_gift_dict.get('found'):
            order_gift_dicts.remove(order_gift_dict)
            unavail_order_gift_dicts.append(unavail_order_gift_dicts)
    for order_gift_dict in cancelled_order_gift_dicts[:]:
        if not order_gift_dict.get('found'):
            cancelled_order_gift_dicts.remove(order_gift_dict)
            unavail_order_gift_dicts.append(unavail_order_gift_dicts)
    response.success = True
    return response


def set_fix_discount(response, outcome, init_total_sum):
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
    points = 0
    for item_dict in item_dicts:
        points += int(point_discount * item_dict['price'])
    if order:
        order.points_details.append(GiftPointsDetails(points=points))
        order.put()
    response.success = True
    return response