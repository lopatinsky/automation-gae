import logging
from models import Order, NEW_ORDER, READY_ORDER, CREATING_ORDER


def check_condition_by_value(condition, value):
    return condition.value == value


def check_condition_max_by_value(condition, value):
    return condition.value > value


def check_condition_min_by_value(condition, value):
    return condition.value < value


def check_first_order(client):
    statuses = [NEW_ORDER, READY_ORDER, CREATING_ORDER]
    order = Order.query(Order.client_id == client.key.id(), Order.status.IN(statuses)).get()
    return order is None


def check_item_in_order(condition, item_dicts):
    amount = 0
    for item_dict in item_dicts:
        if item_dict['item'].key == condition.item:
            amount += 1
    return amount >= condition.value