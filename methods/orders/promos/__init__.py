from models import Promo, PromoCondition, PromoOutcome, STATUS_AVAILABLE
from conditions import check_condition_by_value, check_first_order, check_condition_max_by_value, \
    check_condition_min_by_value, check_item_in_order, check_repeated_order
from outcomes import set_discounts, set_cash_back, set_discount_cheapest, set_discount_richest, set_gift_points, \
    add_order_gift


def _get_initial_total_sum(item_dicts):
    total_sum = 0
    for item_dict in item_dicts:
        total_sum += item_dict['price']
    return total_sum


def _get_promos(venue):
    promos = []
    for promo in Promo.query(Promo.status == STATUS_AVAILABLE).order(-Promo.priority).fetch():
        if promo not in venue.promo_restrictions:
            promos.append(promo)
    return promos


def _check_condition(errors, condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type):
    if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
        return check_condition_by_value(condition, delivery_type)
    if condition.method == PromoCondition.CHECK_FIRST_ORDER:
        return check_first_order(client)
    if condition.method == PromoCondition.CHECK_MAX_ORDER_SUM:
        return check_condition_max_by_value(condition, _get_initial_total_sum(item_dicts))
    if condition.method == PromoCondition.CHECK_ITEM_IN_ORDER:
        return check_item_in_order(condition, item_dicts)
    if condition.method == PromoCondition.CHECK_REPEATED_ORDERS:
        return check_repeated_order(condition, client)


def _set_outcome(errors, outcome, items, promo, client, new_order_gift_dicts, order_gift_dicts,
                 cancelled_order_gift_dicts, order):
    if outcome.method == PromoOutcome.DISCOUNT:
        return set_discounts(outcome, items, promo)
    if outcome.method == PromoOutcome.CASH_BACK:
        return set_cash_back(outcome, items, promo, order)
    if outcome.method == PromoOutcome.DISCOUNT_CHEAPEST:
        return set_discount_cheapest(outcome, items, promo)
    if outcome.method == PromoOutcome.DISCOUNT_RICHEST:
        return set_discount_richest(outcome, items, promo)
    if outcome.method == PromoOutcome.ACCUMULATE_GIFT_POINT:
        return set_gift_points(outcome, items, promo, order)
    if outcome.method == PromoOutcome.ORDER_GIFT:
        return add_order_gift(errors, outcome, promo, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts, order)


def apply_promos(venue, client, item_dicts, payment_info, delivery_time, delivery_type, order_gift_dicts,
                 cancelled_order_gift_dicts, order=None):
    errors = []
    promos = []
    new_order_gift_dicts = []
    for promo in _get_promos(venue):
        apply_promo = True
        for condition in promo.conditions:
            if not _check_condition(errors, condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type):
                apply_promo = False
                break
        if apply_promo:
            for outcome in promo.outcomes:
                if _set_outcome(errors, outcome, item_dicts, promo, client, new_order_gift_dicts, order_gift_dicts,
                                cancelled_order_gift_dicts, order):
                    if promo.key.id() not in promos:
                        promos.append(promo)
    return errors, new_order_gift_dicts, item_dicts, promos