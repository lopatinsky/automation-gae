# coding=utf-8
from Queue import Queue
from datetime import datetime, timedelta

from google.appengine.ext import ndb

from methods import working_hours
from methods.versions import CLIENT_VERSIONS
from models import STATUS_AVAILABLE, Promo, MenuCategory
from models.config.config import Config
from models.geo_push import GeoPush, LeftBasketPromo
from models.order import Order
from models.share import SharedPromo
from outcomes import get_item_dict
from models.order import NOT_CANCELED_STATUSES
from models.promo_code import PromoCodePerforming, KIND_ORDER_PROMO


def _get_category_ids(current_id):
    q = Queue()
    q.put(current_id)
    cats = []
    while not q.empty():
        current_id = q.get()
        cats.append(current_id)
        for category in MenuCategory.query(MenuCategory.category == ndb.Key(MenuCategory, current_id)):
            q.put(category.key.id())
    return cats


def _check_item(item_details, item_dict):
    from methods.orders.validation.validation import is_equal

    if not item_details.item:
        return False
    return is_equal(get_item_dict(item_details), item_dict)


def check_condition_by_value(condition, value):
    return condition.value == value


def check_condition_max_by_value(condition, value):
    return condition.value > value


def check_condition_min_by_value(condition, value):
    return condition.value <= int(value)


def check_registration_date(client, days):
    """Checks, if client registered some days ago"""
    today = datetime.today()
    days_num = (today - client.created).days
    return days_num == days


def check_first_order(client):
    order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()
    return order is None


def check_repeated_order(condition, client):
    if condition.value > 0:
        min_time = datetime.utcnow() - timedelta(days=condition.value)
        order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES),
                            Order.date_created > min_time).get()
    else:
        order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()
    return order is not None


def check_repeated_order_before(condition, client):
    order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()
    if not order:
        return False
    return not check_repeated_order(condition, client)


def check_item_in_order(condition, item_dicts):
    amount = 0
    for item_dict in item_dicts:
        if _check_item(condition.item_details, item_dict):
            amount += 1
    return amount > condition.value


def check_happy_hours_delivery_time(condition, venue, delivery_time):
    now = delivery_time + timedelta(hours=venue.timezone_offset)
    return working_hours.check(condition.schedule, now)


def check_happy_hours_created_time(condition, venue):
    MAX_SECONDS_LOSS = 10
    now = datetime.utcnow() + timedelta(hours=venue.timezone_offset) - timedelta(seconds=MAX_SECONDS_LOSS)
    return working_hours.check(condition.schedule, now)


def check_group_modifier_choice(condition, item_dicts):
    for item_dict in item_dicts:
        if item_dict.get('group_modifier_keys'):
            for modifier in item_dict['group_modifier_keys']:
                if modifier[1] == condition.value:
                    return True
    return False


def check_payment_type(condition, payment_info):
    return check_condition_by_value(condition, payment_info.get('type_id'))


def mark_item_with_category(condition, item_dicts):
    cats = _get_category_ids(condition.value)
    for item_dict in item_dicts:
        if item_dict['item'].category.id() not in cats:
            item_dict['temporary_mark'] = False
    return True


def mark_item_without_category(condition, item_dicts):
    for item_dict in item_dicts:
        if item_dict['item'].category.id() == condition.value:
            item_dict['temporary_mark'] = False
    return True


def mark_item(condition, item_dicts):
    for item_dict in item_dicts:
        if item_dict['item'].key.id() != condition.value:
            item_dict['temporary_mark'] = False
    return True


def mark_not_item(condition, item_dicts):
    for item_dict in item_dicts:
        if item_dict['item'].key.id() == condition.value:
            item_dict['temporary_mark'] = False
    return True


def mark_item_with_quantity(condition, item_dicts):
    from methods.orders.validation.validation import is_equal

    for index1, item_dict1 in enumerate(item_dicts):
        amount = 1
        for index2, item_dict2 in enumerate(item_dicts):
            if index1 != index2 and is_equal(item_dict1, item_dict2):
                amount += 1
            if index1 > index2 and amount == 2:
                amount = 1
                break
        if amount < condition.value:
            item_dict1['temporary_mark'] = False
    return True


def check_marked_quantity(condition, item_dicts):
    amount = 0
    for item_dict in item_dicts:
        if item_dict['persistent_mark']:
            amount += 1
    print "check_marked_quantity, found %s" % amount
    return amount >= condition.value


def check_marked_min_sum(condition, item_dicts):
    marked_sum = 0
    for item_dict in item_dicts:
        if item_dict['persistent_mark']:
            marked_sum += item_dict['price']
    return marked_sum >= condition.value


def check_promo_code(condition, client, order):
    for performing in PromoCodePerforming.query(PromoCodePerforming.client == client.key,
                                                PromoCodePerforming.status == PromoCodePerforming.PROCESSING_ACTION).fetch():
        promo_code = performing.promo_code.get()
        if promo_code.kind == KIND_ORDER_PROMO and promo_code.group_id == condition.value:
            if order:
                performing.put_in_order()
                order.promo_code_performings.append(performing.key)
            return True
    return False


def check_order_number(condition, client):
    orders = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).fetch()
    if (len(orders) + 1) % condition.value == 0:
        return True
    else:
        return False


def check_item_not_in_order(condition, item_dicts):
    amount = 0
    for item_dict in item_dicts:
        if _check_item(condition.item_details, item_dict):
            amount += 1
    return amount == 0


def check_version(condition, client):
    return CLIENT_VERSIONS[condition.value] in client.user_agent


def check_geo_push(client, order):
    push = GeoPush.query(GeoPush.client == client.key, GeoPush.status == STATUS_AVAILABLE).get()
    success = False
    if push:
        config = Config.get()
        last_day = datetime.utcnow() - timedelta(days=config.GEO_PUSH_MODULE.days_without_order)
        last_order = Order.query(Order.date_created > last_day,
                                 Order.client_id == client.key.id(),
                                 Order.status.IN(NOT_CANCELED_STATUSES)).get()
        if not last_order:
            success = True
            if order:
                order.geo_push = push.key
                push.deactivate()
    return success


def check_left_basket_promo(client, order):
    basket_promo = LeftBasketPromo.query(LeftBasketPromo.client == client.key,
                                         LeftBasketPromo.status == STATUS_AVAILABLE).get()
    success = False
    if basket_promo:
        success = True
        if order:
            order.left_basket_promo = basket_promo.key
            basket_promo.deactivate()
    return success


def check_persist_mark(item_dicts):
    for item_dict in item_dicts:
        if item_dict['persistent_mark']:
            return True
    return False



def check_marked_dish_has_not_group_modifiers(condition, item_dicts):
    for item_dict in item_dicts:
        if item_dict.get('group_modifier_keys'):
            for modifier in item_dict['group_modifier_keys']:
                if modifier[1] == condition.value:
                    item_dict['temporary_mark'] = False
    return True

def check_marked_dish_has_group_modifiers(condition, item_dicts):
    for item_dict in item_dicts:
        if item_dict.get('group_modifier_keys'):
            for modifier in item_dict['group_modifier_keys']:
                if modifier[1] == condition.value:
                    break
            else:
                item_dict['temporary_mark'] = False
    return True

def check_max_promo_uses(condition, client):
    promo_key = ndb.Key(Promo, condition.value)
    sum = 0
    for order in Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).fetch():
        if promo_key in order.promos:
            sum += 1
            if sum >= condition.value:
                return False
    return True


def check_min_date(condition, delivery_time):
    condition_date_str = str(condition.value)
    condition_date = datetime.strptime(condition_date_str, "%Y%m%d").date()
    if delivery_time.date() >= condition_date:
        return True
    return False


def check_max_date(condition, delivery_time):
    condition_date_str = str(condition.value)
    condition_date = datetime.strptime(condition_date_str, "%Y%m%d").date()
    if delivery_time.date() <= condition_date:
        return True
    return False


READY = 0
DONE = 1


def check_user_invited_another(client, order):
    shared_promo = SharedPromo.query(SharedPromo.sender == client.key, SharedPromo.status == DONE,
                                     SharedPromo.sender_promo_success == False).get()
    if shared_promo is not None:
        shared_promo.sender_promo_success = True
        if order:
            order.shared_promo = shared_promo.key
            shared_promo.put()
    return shared_promo is not None


def check_user_is_invited(client, order):
    shared_promo = SharedPromo.query(SharedPromo.recipient == client.key, SharedPromo.status == READY,
                                     SharedPromo.recipient_promo_success == False).get()
    if shared_promo is not None:
        shared_promo.recipient_promo_success = True
        if order:
            order.shared_promo = shared_promo.key
            shared_promo.put()
    return shared_promo is not None

