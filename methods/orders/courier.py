# coding=utf-8
from methods import push
from models import Client
from models.order import ON_THE_WAY

__author__ = 'dvpermyakov'


def send_to_courier(order, namespace):
    order.status = ON_THE_WAY
    order.put()

    client = Client.get_by_id(order.client_id)
    text = u"%s, заказ №%s был послан курьеру." % (client.name, order.key.id())
    push.send_order_push(order, text, namespace)