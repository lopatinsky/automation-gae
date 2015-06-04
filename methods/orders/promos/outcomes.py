# coding=utf-8
from models import CashBack, GiftPointsDetails, MenuItem

def _get_item_keys(item_dicts):
    result = {}
    for item_dict in item_dicts:
        if result.get(item_dict['item'].key):
            result[item_dict['item'].key].append(item_dict)
        else:
            result[item_dict['item'].key] = [item_dict]
    return result


def _apply_discounts(item_dict, promo, discount):
        if promo not in item_dict['promos']:
            if item_dict['revenue'] >= item_dict['price'] * discount:
                item_dict['revenue'] -= item_dict['price'] * discount
                item_dict['promos'].append(promo)
                return True
        return False


def _apply_cash_back(item_dict, promo, cash_back, order=None):
        if promo not in item_dict['promos']:
            if order:
                order.cash_backs.append(CashBack(amount=int(cash_back * item_dict['price'] * 100)))
            item_dict['promos'].append(promo)
            return True
        return False


def set_discounts(outcome, item_dicts, promo):
    discount = float(outcome.value) / 100.0
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item):
        for item_dict in item_keys[outcome.item]:
            if _apply_discounts(item_dict, promo, discount):
                promo_applied = True
    if not outcome.item_required:
        for item_dict in item_dicts:
            if _apply_discounts(item_dict, promo, discount):
                promo_applied = True
    return promo_applied


def set_cash_back(outcome, item_dicts, promo, order):
    cash_back = float(outcome.value) / 100.0
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item):
        for item_dict in item_keys[outcome.item]:
            if _apply_cash_back(item_dict, promo, cash_back, order):
                promo_applied = True
    if not outcome.item_required:
        for item_dict in item_dicts:
            if _apply_cash_back(item_dict, promo, cash_back, order):
                promo_applied = True
    if order:
        order.put()
    return promo_applied


def set_discount_cheapest(outcome, item_dicts, promo):
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
    if item_keys.get(outcome.item):  # Not implemented, unfortunately
        pass
    if not outcome.item_required:
        item_dict = get_cheapest(item_dicts)
        if item_dict:
            if _apply_discounts(item_dict, promo, discount):
                promo_applied = True
    return promo_applied


def set_discount_richest(outcome, item_dicts, promo):
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
    if item_keys.get(outcome.item):  # Not implemented, unfortunately
        pass
    if not outcome.item_required:
        item_dict = get_richest(item_dicts)
        if item_dict:
            if _apply_discounts(item_dict, promo, discount):
                promo_applied = True
    return promo_applied


def set_gift_points(outcome, item_dicts, promo, order):
    item_keys = _get_item_keys(item_dicts)
    promo_applied = False
    if item_keys.get(outcome.item):
        for item_dict in item_dicts:
            if item_dict['item'].key == outcome.item:
                if order:
                    order.points_details.append(GiftPointsDetails(item=outcome.item, points=outcome.value))
                    order.put()
                item_dict['promos'].append(promo)
                promo_applied = True
    if not outcome.item_required:
        if order:
            order.points_details.append(GiftPointsDetails(points=outcome.value * len(item_dicts)))
            order.put()
            for item_dict in item_dicts:
                item_dict['promos'].append(promo)
        promo_applied = True
    return promo_applied


def add_order_gift(errors, outcome, promo, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts, order):
    from methods.orders.validation import set_item_dicts
    gift = MenuItem.get_by_id(int(outcome.value))
    if not gift:
        errors.append(u'Акция подарок по заказу не привязана к продукту')
        return False
    found = False
    for order_gift_dict in order_gift_dicts:
        if order_gift_dict['item'].key == gift.key and promo not in order_gift_dict['promos']:
            found = True
            order_gift_dict['promos'].append(promo)
            break
    if not found:
        for order_gift_dict in cancelled_order_gift_dicts:
            if order_gift_dict['item'].key == gift.key and promo not in order_gift_dict['promos']:
                found = True
                order_gift_dict['promos'].append(promo)
                break
    if not found:
        gift.chosen_single_modifiers = []
        gift.chosen_group_modifiers = []
        new_order_gift_dicts.append(set_item_dicts([gift], True)[0])