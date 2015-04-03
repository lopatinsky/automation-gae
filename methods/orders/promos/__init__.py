from models import Promo, PromoCondition, PromoOutcome
from conditions import check_condition_by_value
from outcomes import set_discounts
import logging


def get_promos(venue):
    promos = []
    for promo in Promo.query().fetch():
        if promo not in venue.promo_restrictions:
            promos.append(promo)
    return promos


def check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type):
    if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
        return check_condition_by_value(condition, delivery_type)


def set_outcome(outcome, items, promo):
    if outcome.method == PromoOutcome.DISCOUNT:
        return set_discounts(outcome, items, promo)


def apply_promos(venue, client, item_dicts, payment_info, delivery_time, delivery_type):
    promos = []
    for promo in get_promos(venue):
        apply_promo = True
        for condition in promo.conditions:
            if not check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type):
                apply_promo = False
                break
        if apply_promo:
            for outcome in promo.outcomes:
                if set_outcome(outcome, item_dicts, promo):
                    if promo.key.id() not in promos:
                        promos.append(promo)
    return item_dicts, promos