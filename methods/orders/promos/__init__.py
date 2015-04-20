from models import Promo, PromoCondition, PromoOutcome
from conditions import check_condition_by_value, check_first_order
from outcomes import set_discounts, set_cash_back


def get_promos(venue):
    promos = []
    for promo in Promo.query().fetch():
        if promo not in venue.promo_restrictions:
            promos.append(promo)
    return promos


def check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type):
    if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
        return check_condition_by_value(condition, delivery_type)
    if condition.method == PromoCondition.CHECK_FIRST_ORDER:
        return check_first_order(client)


def set_outcome(outcome, items, promo, client, order):
    if outcome.method == PromoOutcome.DISCOUNT:
        return set_discounts(outcome, items, promo)
    if outcome.method == PromoOutcome.CASH_BACK:
        return set_cash_back(outcome, items, promo, client, order)


def apply_promos(venue, client, item_dicts, payment_info, delivery_time, delivery_type, order=None):
    promos = []
    for promo in get_promos(venue):
        apply_promo = True
        for condition in promo.conditions:
            if not check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type):
                apply_promo = False
                break
        if apply_promo:
            for outcome in promo.outcomes:
                if set_outcome(outcome, item_dicts, promo, client, order):
                    if promo.key.id() not in promos:
                        promos.append(promo)
    return item_dicts, promos