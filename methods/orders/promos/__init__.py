from models import Promo, PromoCondition, PromoOutcome, STATUS_AVAILABLE
from conditions import check_condition_by_value, check_first_order, check_condition_max_by_value, \
    check_condition_min_by_value, check_item_in_order, check_repeated_order, check_happy_hours, \
    check_group_modifier_choice
from outcomes import set_discounts, set_cash_back, set_discount_cheapest, set_discount_richest, set_gift_points, \
    add_order_gift, set_order_gift_points, set_fix_discount, set_delivery_sum_discount


class OutcomeResult:
    def __init__(self):
        self.success = False
        self.discount = 0.0
        self.delivery_sum_discount = 0.0
        self.error = None


def _get_initial_total_sum(item_dicts):
    total_sum = 0
    for item_dict in item_dicts:
        total_sum += item_dict['price']
    return total_sum


def _get_final_total_sum(total_sum, item_dicts):
    for item_dict in item_dicts:
        total_sum -= item_dict['price'] - item_dict['revenue']
    return total_sum


def _get_promos(venue):
    promos = []
    for promo in Promo.query(Promo.status == STATUS_AVAILABLE).order(-Promo.priority).fetch():
        if promo not in venue.promo_restrictions:
            promos.append(promo)
    return promos


def _check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type, total_sum):
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
    if condition.method == PromoCondition.CHECK_MIN_ORDER_SUM:
        return check_condition_min_by_value(condition, _get_initial_total_sum(item_dicts))
    if condition.method == PromoCondition.CHECK_HAPPY_HOURS:
        return check_happy_hours(condition, venue, delivery_time)
    if condition.method == PromoCondition.CHECK_MIN_ORDER_SUM_WITH_PROMOS:
        return check_condition_min_by_value(condition, _get_final_total_sum(total_sum, item_dicts))
    if condition.method == PromoCondition.CHECK_GROUP_MODIFIER_CHOICE:
        return check_group_modifier_choice(condition, item_dicts)
    if condition.method == PromoCondition.CHECK_NOT_GROUP_MODIFIER_CHOICE:
        return not check_group_modifier_choice(condition, item_dicts)


def _set_outcome(outcome, items, promo, client, wallet_payment_sum, delivery_type, delivery_zone,
                 new_order_gift_dicts, unavail_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts, order):
    response = OutcomeResult()
    if outcome.method == PromoOutcome.DISCOUNT:
        return set_discounts(response, outcome, items, promo)
    if outcome.method == PromoOutcome.CASH_BACK:
        return set_cash_back(response, outcome, items, promo, _get_initial_total_sum(items), wallet_payment_sum, order)
    if outcome.method == PromoOutcome.DISCOUNT_CHEAPEST:
        return set_discount_cheapest(response, outcome, items, promo)
    if outcome.method == PromoOutcome.DISCOUNT_RICHEST:
        return set_discount_richest(response, outcome, items, promo)
    if outcome.method == PromoOutcome.ACCUMULATE_GIFT_POINT:
        return set_gift_points(response, outcome, items, promo, order)
    if outcome.method == PromoOutcome.ORDER_GIFT:
        return add_order_gift(response, outcome, promo, new_order_gift_dicts, unavail_order_gift_dicts, order_gift_dicts,
                              cancelled_order_gift_dicts)
    if outcome.method == PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT:
        return set_order_gift_points(response, outcome, order)
    if outcome.method == PromoOutcome.FIX_DISCOUNT:
        return set_fix_discount(response, outcome, _get_initial_total_sum(items))
    if outcome.method == PromoOutcome.DELIVERY_SUM_DISCOUNT:
        return set_delivery_sum_discount(response, outcome, delivery_type, delivery_zone)


def apply_promos(venue, client, item_dicts, payment_info, wallet_payment_sum, delivery_time, delivery_type,
                 delivery_zone, order_gift_dicts, cancelled_order_gift_dicts, order=None):
    total_sum = float(_get_initial_total_sum(item_dicts))
    error = None
    promos = []
    new_order_gift_dicts = []
    unavail_order_gift_dicts = []
    for promo in _get_promos(venue):
        apply_promo = True
        for condition in promo.conditions:
            if not _check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type,
                                    total_sum):
                apply_promo = False
                break
        if apply_promo:
            for outcome in promo.outcomes:
                outcome_response = _set_outcome(outcome, item_dicts, promo, client, wallet_payment_sum, delivery_type,
                                                delivery_zone, new_order_gift_dicts, unavail_order_gift_dicts,
                                                order_gift_dicts, cancelled_order_gift_dicts, order)
                if outcome_response.success:
                    if promo not in promos:
                        promos.append(promo)
                    if outcome_response.discount:
                        total_sum -= outcome_response.discount
                    if outcome_response.delivery_sum_discount:
                        delivery_zone.price = max(int(delivery_zone.price - outcome_response.delivery_sum_discount), 0)
                    if outcome_response.error:
                        error = outcome_response.error
    total_sum = _get_final_total_sum(total_sum, item_dicts)
    total_sum = max(0, total_sum)
    return error, new_order_gift_dicts, unavail_order_gift_dicts, item_dicts, promos, total_sum, delivery_zone