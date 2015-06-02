from datetime import datetime, timedelta
import logging
import re
from google.appengine.api import memcache
from methods.rendering import STR_TIME_FORMAT
from models import Order, Client, Venue, DELIVERY, STATUS_AVAILABLE, DeliverySlot

__author__ = 'dvpermyakov'


def check_order_id(order_id):
    cache_key = "order_%s" % order_id
    if Order.get_by_id(order_id) or not memcache.add(cache_key, 1):
        return False, None
    else:
        return True, cache_key


def check_items_and_gifts(items, gifts):
    if len(items) == 0 and len(gifts) == 0:
        return False
    else:
        return True


def set_client_info(client_json):
    client_id = int(client_json.get('id'))
    if not client_id:
        return None, None
    client = Client.get_by_id(client_id)
    if not client:
        return None, None
    name = client_json.get('name').split(None, 1)
    client_name = name[0]
    client_surname = name[1] if len(name) > 1 else ""
    client_tel = re.sub("[^0-9]", "", client_json.get('phone'))
    client_email = client_json.get('email')
    if client.name != client_name or client.surname != client_surname or client.tel != client_tel \
            or client.email != client_email:
        client.name = client_name
        client.surname = client_surname
        client.tel = client_tel
        client.email = client_email
        client.put()
    return client_id, client


def get_venue_by_address(address):
    for venue in Venue.query().fetch():
        for delivery in venue.delivery_types:
            if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE and not delivery.delivery_zone:
                if address['address']['city'] == venue.address.city:
                    return venue


def get_delivery_time(delivery_time_picker, venue, delivery_slot=None, delivery_time_minutes=None):
    if delivery_time_picker:
        delivery_time_picker = datetime.strptime(delivery_time_picker, STR_TIME_FORMAT)
        if not delivery_slot or delivery_slot.slot_type != DeliverySlot.STRINGS:
            delivery_time_picker -= timedelta(hours=venue.timezone_offset)

    if delivery_slot:
        logging.info(delivery_slot)
        if delivery_slot.slot_type == DeliverySlot.MINUTES:
            delivery_time_minutes = delivery_slot.value
        elif delivery_slot.slot_type == DeliverySlot.STRINGS:
            if delivery_time_picker:
                delivery_time_picker = delivery_time_picker.replace(hour=0, minute=0, second=0)

    delivery_time = None
    if delivery_time_picker:
        delivery_time = delivery_time_picker
    if delivery_time_minutes or delivery_time_minutes == 0:
        if not delivery_time:
            delivery_time = datetime.utcnow()
        delivery_time += timedelta(minutes=delivery_time_minutes)
    logging.info(delivery_time)
    logging.info(delivery_slot)
    return delivery_time