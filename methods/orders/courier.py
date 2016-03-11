# coding=utf-8
from models import Client
from models.order import ON_THE_WAY
from models.push import OrderPush

__author__ = 'dvpermyakov'


def send_to_courier(order, namespace, courier):
    order.status = ON_THE_WAY
    order.courier = courier.key
    order.put()

    client = Client.get(order.client_id)
    text = u"%s, заказ №%s был послан курьеру." % (client.name, order.number)
    OrderPush(text, order, namespace).send()
