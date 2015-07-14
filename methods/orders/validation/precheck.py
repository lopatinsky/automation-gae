from datetime import datetime, timedelta
import logging
import re
from methods.map import get_houses_by_address, get_areas_by_coordinates
from methods.rendering import STR_DATETIME_FORMAT
from models import Order, Client, Venue, STATUS_AVAILABLE, DeliverySlot, DeliveryZone, STATUS_UNAVAILABLE
from models.venue import DELIVERY

__author__ = 'dvpermyakov'


def check_order_id(order_id):
    if order_id:
        order = Order.get_by_id(order_id)
        if order:
            return False, None
        else:
            return True, order_id
    else:
        return True, Order.generate_id()


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


def validate_address(address):
    logging.info('initial address = %s' % address)

    # case of street and home are separated by comma
    if ',' in address['address']['street']:
        address['address']['home'] = address['address']['street'].split(',')[1]
        address['address']['street'] = address['address']['street'].split(',')[0]

    # trim blank spaces
    address['address']['city'] = address['address']['city'].strip()
    address['address']['street'] = address['address']['street'].strip().capitalize()
    address['address']['home'] = address['address']['home'].strip()
    if address['address'].get('flat'):
        address['address']['flat'] = address['address']['flat'].strip()

    # not trust
    address['coordinates']['lat'] = None
    address['coordinates']['lon'] = None

    # try to get coordinates
    candidates = get_houses_by_address(address['address']['city'], address['address']['street'], address['address']['home'])
    for candidate in candidates:
        if candidate['address']['city'].lower() == address['address']['city'].lower():
            if candidate['address']['street'].lower() == address['address']['street'].lower():
                if candidate['address']['home'].lower() == address['address']['home'].lower():
                    address['coordinates']['lat'] = candidate['coordinates']['lat']
                    address['coordinates']['lon'] = candidate['coordinates']['lon']

    logging.info('result address = %s' % address)
    return address


def get_venue_and_zone_by_address(address):
    area = None
    if address:
        has_coords = False
        if address.get('coordinates'):
            if address['coordinates'].get('lat') and address['coordinates'].get('lon'):
                has_coords = True
        # case 1: get venue by city or polygons
        venues = Venue.query(Venue.active == True).fetch()
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([zone_key.get() for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = True  # it is used for mark precise address receipt
                        if zone.search_type == DeliveryZone.CITY:
                            if address['address']['city'] == zone.address.city:
                                return venue, zone
                        elif zone.search_type == DeliveryZone.DISTRICT:
                            if has_coords and zone.address.area:
                                if not area:
                                    candidates = get_areas_by_coordinates(address['coordinates']['lat'],
                                                                          address['coordinates']['lon'])
                                    if candidates:
                                        area = candidates[0]['address']['area']
                                    if not area:
                                        area = u'Not found'
                                if zone.address.area == area:
                                    return venue, zone
                        elif zone.search_type == DeliveryZone.ZONE:
                            if has_coords and zone.is_included(address):
                                return venue, zone
                        elif zone.search_type == DeliveryZone.DEFAULT:
                            return venue, zone
    if not address or\
            not address.get('coordinates') or\
            not address['coordinates'].get('lat') or\
            not address['coordinates'].get('lon') or\
            not area:
        # case 2: get first venue with default flag
        venues = Venue.query(Venue.active == True, Venue.default == True).fetch()
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([zone_key.get() for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = False  # it is used for mark precise address receipt
                        if zone.status == STATUS_AVAILABLE:
                            return venue, zone
        # case 3: get first venue
        venues = Venue.query(Venue.active == True).fetch()
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([zone_key.get() for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = False  # it is used for mark precise address receipt
                        if zone.status == STATUS_AVAILABLE:
                            return venue, zone
    return None, None


def get_delivery_time(delivery_time_picker, venue, delivery_slot=None, delivery_time_minutes=None):
    if delivery_time_picker:
        delivery_time_picker = datetime.strptime(delivery_time_picker, STR_DATETIME_FORMAT)
        if venue and (not delivery_slot or delivery_slot.slot_type != DeliverySlot.STRINGS):
            delivery_time_picker -= timedelta(hours=venue.timezone_offset)

    if delivery_slot:
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
    return delivery_time