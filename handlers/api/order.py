from google.appengine.ext.ndb import GeoPt
from handlers.api.base import ApiHandler
import json
from models import Client, MenuItem, CARD_PAYMENT_TYPE, Order, NEW_ORDER

__author__ = 'ilyazorin'


class OrderHandler(ApiHandler):

    def post(self):
        #TODO errors handling
        response_json = json.loads(self.request.get('order'))
        order_id = response_json['order_id']
        venue_id = response_json['venue_id']
        total_sum = response_json['total_sum']
        coordinates = GeoPt(response_json['coordinates'])
        comment = response_json['comment']
        device_type = response_json['device_type']
        delivery_time = response_json['delivery_time']
        client_id = response_json['client']['client_id']

        client = Client.get_by_id(client_id)
        if not client.name or not client.tel:
            client.name = response_json['client']['name']
            client.tel = response_json['client']['phone']
            client.put()

        items = []
        for item in response_json['items']:
            menu_item = MenuItem.get_by_id(item['item_id'])
            for i in xrange(item['quantity']):
                items.append(menu_item)

        #TODO card payment
        if response_json['payment']['type_id'] == CARD_PAYMENT_TYPE:
            pass

        order = Order(id=order_id, client_id=client_id, venue_id=venue_id, total_sum=total_sum, coordinates=coordinates,
                      comment=comment, status=NEW_ORDER, device_type=device_type, delivery_time=delivery_time,
                      items=[item.key for item in items])
        order.put()

        self.response.status_int = 201
        self.render_json({'order_id': order_id})


class RegisterOrderHandler(ApiHandler):

    def get(self):
        self.render_json({'order_id': Order.generate_id()})
