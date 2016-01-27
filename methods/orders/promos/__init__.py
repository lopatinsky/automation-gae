from methods.orders.promos.conditions import check_left_basket_promo, check_user_invited_another, check_user_is_invited, \
    check_marked_dish_has_group_modifiers, check_marked_dish_has_not_group_modifiers
from methods.orders.promos.outcomes import set_fix_discount_marked_cheapest
from models import Promo, PromoCondition, PromoOutcome, STATUS_AVAILABLE
from conditions import check_condition_by_value, check_first_order, check_condition_max_by_value, \
    check_condition_min_by_value, check_item_in_order, check_repeated_order, check_happy_hours_delivery_time, \
    check_group_modifier_choice, check_payment_type, check_happy_hours_created_time, mark_item_with_category, \
    mark_item_without_category, check_marked_min_sum, mark_item, mark_not_item, mark_item_with_quantity, \
    check_promo_code, check_order_number, check_item_not_in_order, check_marked_quantity, check_version, check_geo_push, \
    check_persist_mark, check_repeated_order_before, check_max_promo_uses, check_min_date, check_max_date, \
    check_registration_date
from outcomes import set_discounts, set_cash_back, set_discount_cheapest, set_discount_richest, set_gift_points, \
    add_order_gift, set_order_gift_points, set_fix_discount, set_delivery_sum_discount, set_delivery_fix_sum_discount, \
    set_percent_gift_points, set_promo_mark_for_marked_items, remove_persistent_mark, add_marked_order_gift, \
    return_success, set_cash_gift_point, forbid_menu_item, set_discount_marked_cheapest, set_delivery_message, \
    set_fix_cash_back, forbid_menu_category, set_marked_discount, set_marked_gift_points


class OutcomeResult:
    def __init__(self):
        self.success = False
        self.discount = 0.0
        self.cash_back = 0.0
        self.delivery_sum_discount = 0.0
        self.error = None


def _set_item_dict(item_dicts):
    for item_dict in item_dicts:
        item_dict['persistent_mark'] = False


def _update_item_dict(item_dicts):
    for item_dict in item_dicts:
        item_dict['temporary_mark'] = True


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



def _check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type, total_sum, order):
    if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
        return check_condition_by_value(condition, delivery_type)
    elif condition.method == PromoCondition.CHECK_FIRST_ORDER:
        return check_first_order(client)
    elif condition.method == PromoCondition.CHECK_MAX_ORDER_SUM:
        return check_condition_max_by_value(condition, _get_initial_total_sum(item_dicts))
    elif condition.method == PromoCondition.CHECK_ITEM_IN_ORDER:
        return check_item_in_order(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_REPEATED_ORDERS:
        return check_repeated_order(condition, client)
    elif condition.method == PromoCondition.CHECK_MIN_ORDER_SUM:
        return check_condition_min_by_value(condition, _get_initial_total_sum(item_dicts))
    elif condition.method == PromoCondition.CHECK_HAPPY_HOURS:
        return check_happy_hours_delivery_time(condition, venue, delivery_time)
    elif condition.method == PromoCondition.CHECK_MIN_ORDER_SUM_WITH_PROMOS:
        return check_condition_min_by_value(condition, _get_final_total_sum(total_sum, item_dicts))
    elif condition.method == PromoCondition.CHECK_GROUP_MODIFIER_CHOICE:
        return check_group_modifier_choice(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_NOT_GROUP_MODIFIER_CHOICE:
        return not check_group_modifier_choice(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_PAYMENT_TYPE:
        return check_payment_type(condition, payment_info)
    elif condition.method == PromoCondition.CHECK_HAPPY_HOURS_CREATED_TIME:
        return check_happy_hours_created_time(condition, venue)
    elif condition.method == PromoCondition.MARK_ITEM_WITH_CATEGORY:
        return mark_item_with_category(condition, item_dicts)
    elif condition.method == PromoCondition.MARK_ITEM_WITHOUT_CATEGORY:
        return mark_item_without_category(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_MARKED_MIN_SUM:
        return check_marked_min_sum(condition, item_dicts)
    elif condition.method == PromoCondition.MARK_ITEM:
        return mark_item(condition, item_dicts)
    elif condition.method == PromoCondition.MARK_NOT_ITEM:
        return mark_not_item(condition, item_dicts)
    elif condition.method == PromoCondition.MARK_ITEM_WITH_QUANTITY:
        return mark_item_with_quantity(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_PROMO_CODE:
        return check_promo_code(condition, client, order)
    elif condition.method == PromoCondition.CHECK_ORDER_NUMBER:
        return check_order_number(condition, client)
    elif condition.method == PromoCondition.CHECK_ITEM_NOT_IN_ORDER:
        return check_item_not_in_order(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_MARKED_QUANTITY:
        return check_marked_quantity(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_DEVICE_TYPE:
        return check_condition_by_value(condition, client.device_type)
    elif condition.method == PromoCondition.CHECK_VERSION:
        return check_version(condition, client)
    elif condition.method == PromoCondition.CHECK_GEO_PUSH:
        return check_geo_push(client, order)
    elif condition.method == PromoCondition.CHECK_VENUE:
        return check_condition_by_value(condition, int(venue.key.id()))
    elif condition.method == PromoCondition.CHECK_MARK:
        return check_persist_mark(item_dicts)
    elif condition.method == PromoCondition.CHECK_REPEATED_ORDER_BEFORE:
        return check_repeated_order_before(condition, client)
    elif condition.method == PromoCondition.CHECK_MAX_USES:
        return check_max_promo_uses(condition, client)
    elif condition.method == PromoCondition.CHECK_MIN_DATE:
        return check_min_date(condition, delivery_time)
    elif condition.method == PromoCondition.CHECK_MAX_DATE:
        return check_max_date(condition, delivery_time)
    elif condition.method == PromoCondition.CHECK_LEFT_BASKET_PROMO:
        return check_left_basket_promo(client, order)
    elif condition.method == PromoCondition.CHECK_INVITED_USER:
        return check_user_invited_another(client, order)
    elif condition.method == PromoCondition.CHECK_USER_INVITED:
        return check_user_is_invited(client, order)
    elif condition.method == PromoCondition.CHECK_DISH_HAS_GROUP_MODIFIERS:
        return check_marked_dish_has_group_modifiers(condition, item_dicts)
    elif condition.method == PromoCondition.CHECK_DISH_HAS_NO_GROUP_MODIFIERS:
        return check_marked_dish_has_not_group_modifiers(condition, item_dicts)
    else:
        return True


def _set_outcome(outcome, items, promo, wallet_payment_sum, delivery_type, delivery_zone, new_order_gift_dicts,
                 order_gift_dicts, cancelled_order_gift_dicts, order):
    response = OutcomeResult()
    if outcome.method == PromoOutcome.DISCOUNT:
        return set_discounts(response, outcome, items, promo)
    elif outcome.method == PromoOutcome.CASH_BACK:
        return set_cash_back(response, outcome, items, promo, _get_initial_total_sum(items), wallet_payment_sum, order)
    elif outcome.method == PromoOutcome.DISCOUNT_CHEAPEST:
        return set_discount_cheapest(response, outcome, items, promo)
    elif outcome.method == PromoOutcome.DISCOUNT_RICHEST:
        return set_discount_richest(response, outcome, items, promo)
    elif outcome.method == PromoOutcome.ACCUMULATE_GIFT_POINT:
        return set_gift_points(response, outcome, items, promo, order)
    elif outcome.method == PromoOutcome.ORDER_GIFT:
        return add_order_gift(response, outcome, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts)
    elif outcome.method == PromoOutcome.ORDER_ACCUMULATE_GIFT_POINT:
        return set_order_gift_points(response, outcome, order)
    elif outcome.method == PromoOutcome.FIX_DISCOUNT:
        return set_fix_discount(response, outcome, promo, items, _get_initial_total_sum(items))
    elif outcome.method == PromoOutcome.DELIVERY_SUM_DISCOUNT:
        return set_delivery_sum_discount(response, outcome, delivery_type, delivery_zone)
    elif outcome.method == PromoOutcome.DELIVERY_FIX_SUM_DISCOUNT:
        return set_delivery_fix_sum_discount(response, outcome, delivery_type, delivery_zone)
    elif outcome.method == PromoOutcome.PERCENT_GIFT_POINT:
        return set_percent_gift_points(response, outcome, items, order)
    elif outcome.method == PromoOutcome.SET_PERSISTENT_MARK:
        return set_promo_mark_for_marked_items(response, items, promo)
    elif outcome.method == PromoOutcome.REMOVE_PERSISTENT_MARK:
        return remove_persistent_mark(response, items, promo)
    elif outcome.method == PromoOutcome.MARKED_ORDER_GIFT:
        return add_marked_order_gift(response, items, new_order_gift_dicts, order_gift_dicts, cancelled_order_gift_dicts)
    elif outcome.method == PromoOutcome.EMPTY:
        return return_success(response)
    elif outcome.method == PromoOutcome.CASH_ACCUMULATE_GIFT_POINT:
        return set_cash_gift_point(response, outcome, _get_final_total_sum(_get_initial_total_sum(items), items), order)
    elif outcome.method == PromoOutcome.FORBID_MENU_ITEM:
        return forbid_menu_item(response, outcome, items)
    elif outcome.method == PromoOutcome.MARKED_DISCOUNT_CHEAPEST:
        return set_discount_marked_cheapest(response, outcome, items, promo)
    elif outcome.method == PromoOutcome.DELIVERY_MESSAGE:
        return set_delivery_message(response, promo, delivery_type, delivery_zone)
    elif outcome.method == PromoOutcome.FIX_CASH_BACK:
        return set_fix_cash_back(response, outcome, order)
    elif outcome.method == PromoOutcome.FORBID_MENU_CATEGORY:
        return forbid_menu_category(response, outcome, items)
    elif outcome.method == PromoOutcome.MARKED_DISCOUNT:
        return set_marked_discount(response, outcome, items, promo)
    elif outcome.method == PromoOutcome.MARKED_ACCUMULATE_GIFT_POINT:
        return set_marked_gift_points(response, outcome, items, promo, order)
    elif outcome.method == PromoOutcome.MARKED_FIX_DISCOUNT_CHEAPEST:
        return set_fix_discount_marked_cheapest(response, outcome, items, promo)
    else:
        response.success = True
        return response


def apply_promos(venue, client, item_dicts, payment_info, wallet_payment_sum, delivery_time, delivery_type,
                 delivery_zone, order_gift_dicts, cancelled_order_gift_dicts, order=None):
    total_sum = float(_get_initial_total_sum(item_dicts))
    _set_item_dict(item_dicts)
    error = None
    promos = []
    new_order_gift_dicts = []
    unavail_order_gift_dicts = []
    cash_back = 0.0
    for promo in _get_promos(venue):
        _update_item_dict(item_dicts)
        apply_promo = True
        for conflict in promo.conflicts:
            if conflict in (promo.key for promo in promos):
                apply_promo = False
        for condition in promo.conditions:
            if not _check_condition(condition, venue, client, item_dicts, payment_info, delivery_time, delivery_type,
                                    total_sum, order):
                apply_promo = False
                break
        if apply_promo:
            for outcome in promo.outcomes:
                outcome_response = _set_outcome(outcome, item_dicts, promo, wallet_payment_sum, delivery_type,
                                                delivery_zone, new_order_gift_dicts, order_gift_dicts,
                                                cancelled_order_gift_dicts, order)
                if outcome_response.success:
                    if promo not in promos:
                        promos.append(promo)
                    if outcome_response.discount:
                        total_sum -= outcome_response.discount
                    if outcome_response.cash_back:
                        cash_back += outcome_response.cash_back
                    if outcome_response.delivery_sum_discount:
                        delivery_zone.price = max(int(delivery_zone.price - outcome_response.delivery_sum_discount), 0)
                    if outcome_response.error:
                        error = outcome_response.error
    for order_gift_dict in order_gift_dicts[:]:
        if not order_gift_dict.get('found'):
            order_gift_dicts.remove(order_gift_dict)
            unavail_order_gift_dicts.append(order_gift_dict)
    for order_gift_dict in cancelled_order_gift_dicts[:]:
        if not order_gift_dict.get('found'):
            cancelled_order_gift_dicts.remove(order_gift_dict)
            unavail_order_gift_dicts.append(order_gift_dict)
    total_sum = _get_final_total_sum(total_sum, item_dicts)
    total_sum = max(0, total_sum)
    return error, new_order_gift_dicts, unavail_order_gift_dicts, item_dicts, promos, total_sum, cash_back, delivery_zone