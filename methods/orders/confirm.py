# coding=utf-8
from models import Client
from models.order import CONFIRM_ORDER
from models.push import OrderPush

__author__ = 'dvpermyakov'


def confirm_order(order, namespace):
    order.status = CONFIRM_ORDER
    order.email_key_confirm = None
    order.put()

    client = Client.get(order.client_id)
    text = u"%s, заказ №%s был подтвержден." % (client.name, order.number)
    OrderPush(text, order, namespace).send()
