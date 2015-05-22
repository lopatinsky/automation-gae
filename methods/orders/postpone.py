# coding=utf-8
from datetime import timedelta
from methods import push
from models import Venue, Client

__author__ = 'dvpermyakov'


def postpone_order(order, minutes):
    order.delivery_time += timedelta(minutes=minutes)
    order.put()

    venue = Venue.get_by_id(order.venue_id)
    local_delivery_time = order.delivery_time + timedelta(hours=venue.timezone_offset)
    time_str = local_delivery_time.strftime("%H:%M")
    client = Client.get_by_id(order.client_id)
    push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order.key.id(), time_str)
    push.send_order_push(order.key.id(), order.status, push_text, order.device_type, new_time=order.delivery_time)