# coding=utf-8
from datetime import timedelta
from methods import push
from methods.rendering import STR_TIME_FORMAT, STR_DATE_FORMAT
from models import Venue, Client, DeliverySlot

__author__ = 'dvpermyakov'


def postpone_order(order, minutes):
    order.delivery_time += timedelta(minutes=minutes)

    venue = Venue.get_by_id(order.venue_id)
    local_delivery_time = order.delivery_time + timedelta(hours=venue.timezone_offset)

    delivery_slot = None
    if order.delivery_slot_id:
        delivery_slot = DeliverySlot.get_by_id(order.delivery_slot_id)
    if delivery_slot and delivery_slot.slot_type == DeliverySlot.STRINGS:
        delivery_time_str = local_delivery_time.strftime(STR_DATE_FORMAT)
    else:
        delivery_time_str = local_delivery_time.strftime(STR_TIME_FORMAT)
    order.delivery_time_str = delivery_time_str
    order.put()

    time_str = local_delivery_time.strftime("%H:%M")
    client = Client.get_by_id(order.client_id)
    push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order.key.id(), time_str)
    push.send_order_push(order.key.id(), order.status, push_text, order.device_type, new_time=order.delivery_time)