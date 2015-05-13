from models import Order, STATUS_AVAILABLE


def check_condition_by_value(condition, value):
    return condition.value == value


def check_condition_max_by_value(condition, value):
    return condition.value > value


def check_condition_min_by_value(condition, value):
    return condition.value < value


def check_first_order(client):
    order = Order.query(Order.client_id == client.key.id(), Order.status == STATUS_AVAILABLE).get()
    return order is None