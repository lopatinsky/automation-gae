# coding=utf-8
from methods import push
from models import CONFIRM_ORDER, Client

__author__ = 'dvpermyakov'


def confirm_order(order):
    order.status = CONFIRM_ORDER
    order.put()

    client = Client.get_by_id(order.client_id)
    text = u"%s, заказ №%s был подтвержден." % (client.name, order.key.id())
    push.send_order_push(order.key.id(), order.status, text, order.device_type)