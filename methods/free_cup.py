__author__ = 'dvpermyakov'

from models import Order


def get_master_bonus(client):
    if client.has_mastercard_orders:
        orders = Order.query(Order.client_id == client.key.id()).fetch()
        result = 0
        for order in orders:
            if order.mastercard:
                result += 1
        return result
    else:
        return 0