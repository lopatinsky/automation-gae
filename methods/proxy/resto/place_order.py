from datetime import datetime
from methods.rendering import STR_DATETIME_FORMAT
from models.proxy.resto import RestoClient
from requests import post_resto_place_order

__author__ = 'dvpermyakov'


def resto_place_order(client, venue, order, payment_json):
    resto_client = RestoClient.query(RestoClient.client == client.key).get()
    resto_place_result = post_resto_place_order(venue, resto_client, client, order, payment_json)
    if resto_place_result.get('error') and resto_place_result['error'] == True:
        success = False
        response = {
            'description': resto_place_result['description']
        }
    else:
        success = True
        response = {
            'order_id': order.key.id(),
            'delivery_time': datetime.strftime(order.delivery_time, STR_DATETIME_FORMAT),
            'delivery_slot_name': None
        }
    return success, response
