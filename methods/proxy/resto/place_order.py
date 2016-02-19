import uuid
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from methods.orders.validation.validation import get_order_position_details
from methods.proxy.resto.check_order import get_resto_address_dict, get_resto_item_dicts, get_item_and_item_dicts, \
    get_init_total_sum
from methods.rendering import STR_DATETIME_FORMAT
from models import Order
from models.order import NEW_ORDER, CREATING_ORDER
from models.proxy.resto import RestoClient, RestoCompany
from models.venue import DELIVERY
from requests import post_resto_place_order

__author__ = 'dvpermyakov'


def resto_place_order(client, venue, order, payment_json, items_json, order_gifts, cancelled_order_gifts):
    resto_company = RestoCompany.get()
    resto_client = RestoClient.get(client)
    if order.delivery_type == DELIVERY:
        resto_address_dict = get_resto_address_dict(order.address)
    else:
        resto_address_dict = {}
    items, item_dicts = get_item_and_item_dicts(items_json, venue)
    resto_item_dicts = get_resto_item_dicts(items_json)
    resto_gift_dicts = get_resto_item_dicts(order_gifts)
    order.init_total_sum = get_init_total_sum(items)
    order.item_details = get_order_position_details(item_dicts)
    local_delivery_time = order.delivery_time + timedelta(hours=venue.timezone_offset)
    order.delivery_time_str = local_delivery_time.strftime(STR_DATETIME_FORMAT)

    if not order.extra_data:
        order.extra_data = {}
    order_uuid = order.extra_data['iiko_uuid'] = str(uuid.uuid4())

    order.status = CREATING_ORDER
    order.put()

    resto_place_result = post_resto_place_order(resto_company, venue, resto_client, client, order, resto_item_dicts,
                                                resto_gift_dicts,
                                                payment_json, resto_address_dict, order_uuid)

    if resto_place_result.get('error') == True or resto_place_result.get('code') == '100':
        success = False
        response = {
            'description': resto_place_result['description']
        }
    else:
        resto_client.resto_customer_id = resto_place_result['customer_id']
        resto_client.put()
        old_key = order.key
        order.key = ndb.Key(Order, resto_place_result['order']['resto_id'])
        order.number = int(resto_place_result['order']['number'])
        order.status = NEW_ORDER
        order.put()
        old_key.delete()
        success = True

        response = {
            'order_id': order.key.id(),
            'number': order.number,
            'delivery_time': order.delivery_time_str,
            'delivery_slot_name': None,
            'show_share': False,
        }
    return success, response
