from datetime import datetime
from google.appengine.ext import ndb
from methods.proxy.resto.check_order import get_resto_address_dict, get_resto_item_dicts
from methods.rendering import STR_DATETIME_FORMAT
from models import Order
from models.order import NEW_ORDER
from models.proxy.resto import RestoClient
from requests import post_resto_place_order

__author__ = 'dvpermyakov'


def resto_place_order(client, venue, order, payment_json, items_json, address_json):
    resto_client = RestoClient.get(client)
    resto_address_dict = get_resto_address_dict(address_json)
    resto_item_dicts = get_resto_item_dicts(items_json)
    resto_place_result = post_resto_place_order(venue, resto_client, client, order, resto_item_dicts, payment_json,
                                                resto_address_dict)
    if resto_place_result.get('error') and resto_place_result['error'] == True:
        success = False
        response = {
            'description': resto_place_result['description']
        }
    else:
        resto_client.resto_customer_id = resto_place_result['customer_id']
        resto_client.put()
        order.key = ndb.Key(Order, resto_place_result['order']['number'])
        order.status = NEW_ORDER
        order.put()
        success = True
        response = {
            'order_id': order.key.id(),
            'delivery_time': datetime.strftime(order.delivery_time, STR_DATETIME_FORMAT),
            'delivery_slot_name': None
        }
    return success, response