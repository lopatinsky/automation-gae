from datetime import timedelta
from google.appengine.ext import ndb
from methods.orders.validation.validation import get_order_position_details
from methods.proxy.doubleb.check_order import get_doubleb_delivery_time, update_payment_info, get_doubleb_item_dicts, \
    get_auto_item_dicts
from methods.proxy.doubleb.requests import post_doubleb_place_order
from methods.rendering import STR_DATETIME_FORMAT
from models import Order
from models.order import NEW_ORDER
from models.proxy.doubleb import DoublebCompany, DoublebClient

__author__ = 'dvpermyakov'


def doubleb_place_order(order, client, venue, items, payment):
    company = DoublebCompany.get()
    doubleb_client = DoublebClient.get(client)
    doubleb_response = post_doubleb_place_order(company, order, client, doubleb_client, venue,
                                                get_doubleb_item_dicts(items),
                                                update_payment_info(payment),
                                                get_doubleb_delivery_time(order.delivery_time))
    if doubleb_response.get('description'):
        success = False
        response = {
            'description': doubleb_response['description']
        }
    else:
        success = True
        order.key = ndb.Key(Order, doubleb_response['order_id'])
        order.number = order.key.id()
        order.status = NEW_ORDER
        order.item_details = get_order_position_details(get_auto_item_dicts(items))
        local_delivery_time = order.delivery_time + timedelta(hours=venue.timezone_offset)
        order.delivery_time_str = local_delivery_time.strftime(STR_DATETIME_FORMAT)
        order.put()
        response = {
            'order_id': order.key.id(),
            'number': order.number,
            'delivery_time': order.delivery_time_str,
            'delivery_slot_name': None,
            'show_share': False,
        }
    return success, response
