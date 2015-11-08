# coding=utf-8
from methods import push
from models import Client
from models.order import CONFIRM_ORDER

__author__ = 'dvpermyakov'


def confirm_order(order, namespace):
    order.status = CONFIRM_ORDER
    order.email_key_confirm = None
    order.put()

    client = Client.get(order.client_id)
    text = u"%s, заказ №%s был подтвержден." % (client.name, order.number)
    push.send_order_push(order, text, namespace)