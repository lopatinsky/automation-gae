from datetime import datetime, timedelta
import logging
from models import Order
from models.order import NOT_CANCELED_STATUSES


def check_condition_by_value(condition, value):
    return condition.value == value


def check_condition_max_by_value(condition, value):
    return condition.value > value


def check_condition_min_by_value(condition, value):
    return condition.value < value


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
        if item_dict['item'].key == condition.item:
            amount += 1
    return amount >= condition.value