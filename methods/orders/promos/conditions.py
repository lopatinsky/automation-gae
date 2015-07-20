from datetime import datetime, timedelta
import logging
from methods import working_hours
from models import Order
from models.order import NOT_CANCELED_STATUSES


def _check_item(condition, item_dict):
    if item_dict['item'].key != condition.item_details.item:
        return False
    item_choice_ids = [modifier_key[1] for modifier_key in item_dict['group_modifier_keys']]
    for choice_id in condition.item_details.group_choice_ids:
        if choice_id not in item_choice_ids:
            return False
    return True


def check_condition_by_value(condition, value):
    return condition.value == value


def check_condition_max_by_value(condition, value):
    return condition.value > value


def check_condition_min_by_value(condition, value):
    return condition.value <= int(value)


def check_first_order(client):
    order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()
    return order is None


def check_repeated_order(condition, client):
    if condition.value is not None:
        min_time = datetime.utcnow() - timedelta(days=condition.value)
        order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES),
                            Order.date_created > min_time).get()
    else:
        order = Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()
    logging.info(order)
    return order is not None


def check_item_in_order(condition, item_dicts):
    amount = 0
    for item_dict in item_dicts:
        if _check_item(condition, item_dict):
            amount += 1
    return amount >= condition.value


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