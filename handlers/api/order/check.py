import json
import logging
from google.appengine.api.namespace_manager import namespace_manager
from handlers.api.base import ApiHandler
from methods.emails.admins import send_error
from methods.orders.validation.precheck import validate_address, get_venue_and_zone_by_address, get_delivery_time
from methods.orders.validation.validation import validate_order
from methods.proxy.doubleb.check_order import doubleb_validate_order
from methods.proxy.resto.check_order import resto_validate_order
from models import Client, Venue, DeliverySlot
from models.config.config import AUTO_APP, RESTO_APP, config, DOUBLEB_APP
from models.venue import SELF, PICKUP, DELIVERY
from models.venue import IN_CAFE

__author__ = 'dvpermyakov'

#  all required fields should invoke 400
#  all errors should be catch in validate_order

#  venue can be None         => send error
#  delivery time can be None => send error
#  address can be None       => send error
#  payment can be None       => send error

#  delivery slot can't be None => it violates logic
#  client can't be None        => it violates logic


class CheckOrderHandler(ApiHandler):
    def post(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id') or 0)
        client = Client.get(client_id)
        if not client:
            self.abort(400)

        delivery_type = int(self.request.get('delivery_type'))

        venue = None
        delivery_zone = None
        address = self.request.get('address')

        if delivery_type in [SELF, IN_CAFE, PICKUP]:
            venue_id = self.request.get('venue_id')
            if not venue_id or venue_id == '-1':
                venue = None
            else:
                venue = Venue.get(venue_id)
        elif delivery_type in [DELIVERY]:
            if address:
                address = json.loads(address)
                address = validate_address(address)
            venue, delivery_zone = get_venue_and_zone_by_address(address)

        raw_payment_info = self.request.get('payment')
        payment_info = None
        if raw_payment_info:
            payment_info = json.loads(raw_payment_info)
            if (not payment_info.get('type_id') and payment_info.get('type_id') != 0) or \
                            payment_info.get('type_id') == -1:
                payment_info = None

        delivery_slot_id = self.request.get('delivery_slot_id')
        if delivery_slot_id == '-1':
            self.abort(400)
        if delivery_slot_id:
            delivery_slot_id = int(delivery_slot_id)
            delivery_slot = DeliverySlot.get_by_id(delivery_slot_id)
            if not delivery_slot:
                self.abort(400)
        else:
            delivery_slot = None

        delivery_time_minutes = self.request.get('delivery_time')     # used for old versions todo: remove
        if delivery_time_minutes:                                     # used for old versions todo: remove
            send_error('minutes', 'delivery_time field in check order',
                       'The field is invoked in %s' % namespace_manager.get_namespace())
            delivery_time_minutes = int(delivery_time_minutes)        # used for old versions todo: remove
        delivery_time_picker = self.request.get('time_picker_value')

        delivery_time = get_delivery_time(delivery_time_picker, venue, delivery_slot, delivery_time_minutes)

        items = json.loads(self.request.get('items'))
        if self.request.get('gifts'):
            gifts = json.loads(self.request.get('gifts'))
        else:
            gifts = []
        if self.request.get('order_gifts'):
            order_gifts = json.loads(self.request.get('order_gifts'))
        else:
            order_gifts = []
        if self.request.get('cancelled_order_gifts'):
            cancelled_order_gifts = json.loads(self.request.get('cancelled_order_gifts'))
        else:
            cancelled_order_gifts = []
        client.save_session(True, bool(items or gifts or order_gifts))

        extra_fields = json.loads(self.request.get('extra_order_fields', '{}'))  # todo: it can be checked in validation

        if config.APP_KIND == AUTO_APP:
            result = validate_order(client, items, gifts, order_gifts, cancelled_order_gifts, payment_info, venue,
                                    address, delivery_time, delivery_slot, delivery_type, delivery_zone)
        elif config.APP_KIND == RESTO_APP:
            result = resto_validate_order(client, items, venue, delivery_time, order_gifts, cancelled_order_gifts,
                                          delivery_type)
        elif config.APP_KIND == DOUBLEB_APP:
            result = doubleb_validate_order(client, venue, items, payment_info, delivery_time)
        else:
            result = {}

        logging.info('validation result = %s' % result)
        self.render_json(result)
