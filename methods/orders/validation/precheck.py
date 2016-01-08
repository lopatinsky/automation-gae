# coding=utf-8
from datetime import datetime, timedelta
import logging
from google.appengine.api import memcache

from google.appengine.ext.ndb import GeoPt
import time

from models.config.config import config
from methods import location
from methods.geocoder import get_houses_by_address, get_areas_by_coordinates
from methods.orders.validation.validation import get_first_error
from methods.rendering import latinize, get_phone, get_separated_name_surname, \
    parse_time_picker_value, get_device_type
from models import Order, Client, Venue, STATUS_AVAILABLE, DeliverySlot, DeliveryZone, STATUS_UNAVAILABLE
from models.order import NOT_CANCELED_STATUSES
from models.venue import DELIVERY

__author__ = 'dvpermyakov'


def get_order_id(order_json):
    def _cache_key(order_id):
        return "order_%s" % order_id

    def _check(order_id, cache_key):
        if Order.get_by_id(order_id) or not memcache.add(cache_key, 1):
            logging.warning("order_id check: %s is in use", order_id)
            return False
        return True

    order_id = order_json.get('order_id')
    if order_id:
        logging.debug("order_id check: got %s from json", order_id)
        order_id = int(order_id)
        cache_key = _cache_key(order_id)
        return order_id, cache_key if _check(order_id, cache_key) else None, None
    else:
        for _ in xrange(3):
            order_id = Order.generate_id()
            cache_key = _cache_key(order_id)
            logging.debug("order_id check: generated %s", order_id)
            if _check(order_id, cache_key):
                return order_id, cache_key
            time.sleep(0.05)  # sleep 50ms for fastcounter
        return None, None


def set_extra_order_info(order, extra_info, num_people, cash_change):
    extra_json = {}
    if config.ORDER_MODULE and config.ORDER_MODULE.status == STATUS_AVAILABLE:
        for field in config.ORDER_MODULE.extra_fields:
            group_key = latinize(field.group_title)
            field_key = latinize(field.title)
            group_dict = extra_info.get(group_key)
            value = group_dict.get(field_key) if group_dict else None
            extra_json[field_key] = value
        if config.ORDER_MODULE.enable_number_of_people:
            extra_info['num_people'] = num_people
        if config.ORDER_MODULE.enable_change:
            extra_info['cash_change'] = cash_change
    order.extra_data = extra_json


def check_items_and_gifts(order_json):
    if not order_json['items'] and not order_json.get('gifts') and not order_json.get('order_gifts'):
        return False
    else:
        return True


def set_client_info(client_json, headers):
    client_id = int(client_json.get('id', 0)) or int(headers.get('Client-Id') or 0)
    if not client_id:
        return None
    client = Client.get(client_id)
    if not client:
        return None
    name, surname = get_separated_name_surname(client_json.get('name'))
    client.name = name
    client.surname = surname
    client.tel = get_phone(client_json.get('phone'))
    client.email = client_json.get('email')
    client.user_agent = headers['User-Agent']
    if not client.device_type:
        client.device_type = get_device_type(client.user_agent)
    client.version = headers.get('Version', 0)
    extra_json = {}
    groups = client_json.get('groups') or {}
    if config.CLIENT_MODULE and config.CLIENT_MODULE.status == STATUS_AVAILABLE:
        for field in config.CLIENT_MODULE.extra_fields:
            group_key = latinize(field.group_title)
            field_key = latinize(field.title)
            group_dict = groups.get(group_key)
            value = group_dict.get(field_key) if group_dict else None
            extra_json[field_key] = value
    client.extra_data = extra_json
    client.put()
    return client


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
        venues = Venue.fetch_venues(Venue.active == True)
        nearest_venues = []  # it is used for getting nearest venue if zone is not found
        # case 1: get venue by polygons or radius
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([DeliveryZone.get(zone_key) for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = True
                        if zone.search_type == DeliveryZone.ZONE:
                            if has_coords and zone.is_included(address):
                                return venue, zone
                        elif zone.search_type == DeliveryZone.RADIUS:
                            if has_coords:
                                distance = location.distance(
                                    GeoPt(address['coordinates']['lat'], address['coordinates']['lon']),
                                    GeoPt(zone.address.lat, zone.address.lon))
                                if distance <= zone.value:
                                    return venue, zone
                        elif zone.search_type == DeliveryZone.NEAREST:
                            if has_coords:
                                venue.distance = location.distance(
                                    GeoPt(address['coordinates']['lat'], address['coordinates']['lon']), venue.coordinates)
                                venue.zone = zone
                                nearest_venues.append(venue)

        # case 2: get venue by district
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([DeliveryZone.get(zone_key) for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = True
                        if zone.search_type == DeliveryZone.DISTRICT:
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

        # case 3: get venue by city
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([DeliveryZone.get(zone_key) for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = True
                        if zone.search_type == DeliveryZone.CITY:
                            if address['address']['city'] == zone.address.city:
                                return venue, zone

        # case 4: get venue by default
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([DeliveryZone.get(zone_key) for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = False
                        if zone.search_type == DeliveryZone.DEFAULT:
                            return venue, zone

        # case 5: get nearest venue
        if nearest_venues:
            venue = sorted(nearest_venues, key=lambda venue: venue.distance)[0]
            return venue, venue.zone

    if not address or\
            not address.get('coordinates') or\
            not address['coordinates'].get('lat') or\
            not address['coordinates'].get('lon') or\
            not area:
        # case 6: get first venue with default flag
        venues = Venue.fetch_venues(Venue.active == True, Venue.default == True)
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([DeliveryZone.get(zone_key) for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = False  # it is used for mark precise address receipt
                        if zone.status == STATUS_AVAILABLE:
                            return venue, zone
        # case 7: get first venue
        venues = Venue.fetch_venues(Venue.active == True)
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.delivery_type == DELIVERY and delivery.status == STATUS_AVAILABLE:
                    for zone in sorted([DeliveryZone.get(zone_key) for zone_key in delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.status == STATUS_UNAVAILABLE:
                            continue
                        zone.found = False  # it is used for mark precise address receipt
                        if zone.status == STATUS_AVAILABLE:
                            return venue, zone
    return None, None


def get_delivery_time(delivery_time_picker, venue, delivery_slot=None, delivery_time_minutes=None):
    if delivery_time_picker:
        delivery_time_picker = parse_time_picker_value(delivery_time_picker)
        if venue and (not delivery_slot or delivery_slot.slot_type == DeliverySlot.MINUTES):
            delivery_time_picker -= timedelta(hours=venue.timezone_offset)

    if delivery_slot:
        if delivery_slot.slot_type == DeliverySlot.MINUTES:
            delivery_time_minutes = delivery_slot.value
            delivery_time_picker = datetime.utcnow()
        elif delivery_slot.slot_type == DeliverySlot.HOURS_FROM_MIDNIGHT:
            if venue:
                tz = venue.timezone_offset
            else:
                tz = Venue.get_first_tz()
            if not delivery_time_picker:
                delivery_time_picker = datetime.now(tz=tz)
            delivery_time_picker = delivery_time_picker.replace(hour=0, minute=0, second=0, microsecond=0)
            delivery_time_picker += timedelta(hours=delivery_slot.value - tz)
            delivery_time_picker += timedelta(seconds=1)  # it is need for being after specific hour in schedule
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
    return delivery_time


def check_after_error(order_json, client):
    MINUTES = 1
    min_ago = datetime.utcnow() - timedelta(minutes=MINUTES)
    previous_order = Order.query(Order.client_id == client.key.id(),
                                 Order.status.IN(NOT_CANCELED_STATUSES),
                                 Order.date_created >= min_ago).get()
    if not previous_order:
        return False
    group_details = Order.grouped_item_dict(previous_order.item_details)
    if len(order_json['items']) != len(group_details):
        return False
    for index, item_detail in enumerate(group_details):
        item_dict = order_json['items'][index]
        if item_dict['item_id'] != item_detail['id'] or item_dict['quantity'] != item_detail['quantity']:
            return False
    return True


def after_validation_check(validation_result, order):
    if not validation_result['valid']:
        logging.warning('Fail in validation')
        return False, get_first_error(validation_result)

    total_sum = validation_result['total_sum']
    delivery_sum = validation_result['delivery_sum']
    if order.total_sum and round(total_sum * 100) != round(order.total_sum * 100):
        return False, u"Сумма заказа была пересчитана"
    if not order.delivery_sum:
        order.delivery_sum = delivery_sum
    if order.delivery_sum and round(delivery_sum * 100) != round(order.delivery_sum * 100):
        return False, u"Сумма доставки была пересчитана"
    if order.wallet_payment and round(order.wallet_payment * 100) != round(validation_result['max_wallet_payment'] * 100):
        return False, u"Сумма оплаты баллами была пересчитана"
    if validation_result['unavail_order_gifts'] or validation_result['new_order_gifts']:
        return False, u"Подарки были пересчитаны"
    return True, None
