# coding:utf-8
import copy
import logging
import json
from datetime import datetime, timedelta

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from google.appengine.ext.ndb import GeoPt

from config import config, AUTO_APP, RESTO_APP
from handlers.api.base import ApiHandler
from methods import empatika_promos, empatika_wallet
from methods.orders.create import send_venue_sms, send_venue_email, send_client_sms, card_payment_performing, \
    paypal_payment_performing, set_address_obj
from methods.orders.validation.validation import validate_order
from methods.orders.cancel import cancel_order
from methods.orders.validation.precheck import get_order_id, set_client_info, get_venue_and_zone_by_address,\
    check_items_and_gifts, get_delivery_time, validate_address, check_after_error, after_validation_check
from methods.proxy.resto.check_order import resto_validate_order
from methods.proxy.resto.place_order import resto_place_order
from models import DeliverySlot, PaymentType, Order, Venue, Client, STATUS_UNAVAILABLE
from models.client import IOS_DEVICE
from models.order import NEW_ORDER, CREATING_ORDER, CANCELED_BY_CLIENT_ORDER, CONFUSED_CHOICES, \
    CONFUSED_OTHER
from models.payment_types import CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE
from models.venue import SELF, IN_CAFE, DELIVERY, PICKUP


class OrderHandler(ApiHandler):
    order = None

    def render_error(self, description):
        if self.order:
            self.order.key.delete()
        self.response.set_status(400)
        logging.warning('error: %s' % description)
        self.render_json({
            'title': u'Ошибка',
            'description': description
        })

    def post(self):
        order_json = json.loads(self.request.get('order'))

        order_id = get_order_id(order_json)
        if not order_id:
            self.abort(409)
        self.order = Order(id=order_id)
        self.order.number = order_id

        success = check_items_and_gifts(order_json)
        if not success:
            return self.render_error(u'Выберите что-нибудь')

        self.order.delivery_type = int(order_json.get('delivery_type'))

        venue = None
        delivery_zone = None
        address_json = order_json.get('address')
        if self.order.delivery_type in [SELF, IN_CAFE, PICKUP]:
            venue_id = order_json.get('venue_id')
            if not venue_id:
                return self.render_error(u"Произошла ошибка. Попробуйте выбрать заново выбрать точку.")
            venue_id = int(venue_id)
            venue = Venue.get_by_id(venue_id)
            if not venue:
                return self.render_error(u"Кофейня не найдена")
        elif self.order.delivery_type in [DELIVERY]:
            if address_json:
                address_json = validate_address(address_json)
                venue, delivery_zone = get_venue_and_zone_by_address(address_json)
        self.order.venue_id = venue.key.id()

        if address_json:
            set_address_obj(address_json, self.order)

        coordinates = order_json.get('coordinates')
        if coordinates:
            self.order.coordinates = GeoPt(coordinates)

        self.order.comment = order_json['comment']
        self.order.device_type = order_json.get('device_type', IOS_DEVICE)

        self.order.delivery_slot_id = int(order_json.get('delivery_slot_id')) \
            if order_json.get('delivery_slot_id') else None
        if self.order.delivery_slot_id == -1:
            return self.render_error(u'Неверно выбран слот времени')
        if self.order.delivery_slot_id:
            delivery_slot = DeliverySlot.get_by_id(self.order.delivery_slot_id)
            if not delivery_slot:
                return self.render_error(u'Неправильный формат времени')
        else:
            delivery_slot = None

        delivery_time_minutes = order_json.get('delivery_time')    # used for old versions todo: remove
        if delivery_time_minutes:                                     # used for old versions todo: remove
            delivery_time_minutes = int(delivery_time_minutes)        # used for old versions todo: remove
        delivery_time_picker = order_json.get('time_picker_value')

        self.order.delivery_time = get_delivery_time(delivery_time_picker, venue, delivery_slot, delivery_time_minutes)
        if not self.order.delivery_time:
            return self.render_error(u'Неправильный формат времени')

        self.order.total_sum = float(order_json.get("total_sum"))
        self.order.delivery_sum = int(order_json.get('delivery_sum', 0))

        client = set_client_info(order_json.get('client'), self.order)
        if not client:
            return self.render_error(u'Неудачная попытка авторизации. Попробуйте позже')
        self.order.client_id = client.key.id()
        self.order.user_agent = self.request.headers["User-Agent"]

        self.order.payment_type_id = order_json['payment']['type_id']
        payment_type = PaymentType.get(self.order.payment_type_id)
        if payment_type.status == STATUS_UNAVAILABLE:
            return self.render_error(u"Выбранный способ оплаты недоступен.")

        self.order.wallet_payment = order_json['payment'].get('wallet_payment', 0)

        if check_after_error(order_json, client):
            return self.render_error(u"Этот заказ уже зарегистрирован в системе, проверьте историю заказов.")

        if config.APP_KIND == RESTO_APP:
            success, response = resto_place_order(client, venue, self.order, order_json['payment'], order_json['items'])
            if success:
                return self.render_json(response)
            else:
                return self.render_error(response['description'])

        # it is need, because item_id and gift_id are swapping
        gifts_copy = copy.deepcopy(order_json.get('gifts', []))

        validation_result = validate_order(client,
                                           order_json['items'],
                                           order_json.get('gifts', []),
                                           order_json.get('order_gifts', []),
                                           order_json.get('cancelled_order_gifts', []),
                                           order_json['payment'],
                                           venue, address_json, self.order.delivery_time, delivery_slot,
                                           self.order.delivery_type,
                                           delivery_zone, True)

        success, error = after_validation_check(validation_result, self.order)
        if not success:
            return self.render_error(error)

        if self.order.delivery_sum:
            self.order.total_sum += self.order.delivery_sum

        self.order.item_details = validation_result["details"]
        self.order.order_gift_details = validation_result["order_gift_details"]
        self.order.shared_gift_details = validation_result['share_gift_details']
        self.order.promo_list = [ndb.Key('Promo', promo['id']) for promo in validation_result["promos"]]
        self.order.delivery_time_str = validation_result['delivery_time']

        self.order.status = CREATING_ORDER
        self.order.put()

        payment_amount = int((self.order.total_sum - self.order.wallet_payment) * 100)

        if self.order.payment_type_id == CARD_PAYMENT_TYPE and payment_amount > 0:
            success, error = card_payment_performing(order_json['payment'], payment_amount, self.order)
            if not success:
                return self.render_error(error)
        elif self.order.payment_type_id == PAYPAL_PAYMENT_TYPE and payment_amount > 0:
            success, error = paypal_payment_performing(order_json['payment'], payment_amount, self.order, client)
            if not success:
                return self.render_json(error)

        if self.order.wallet_payment > 0:
            empatika_wallet.pay(client.key.id(), self.order.key.id(), int(self.order.wallet_payment * 100))

        gift_details = []
        for gift_detail in validation_result['gift_details']:
            gift_item = gift_detail.gift.get()
            activation_dict = empatika_promos.activate_promo(client.key.id(), gift_item.promo_id, 1)
            gift_detail.activation_id = activation_dict['activation']['id']
            gift_details.append(gift_detail)
        self.order.gift_details = gift_details

        for shared_gift_detail in self.order.shared_gift_details:
            gift = shared_gift_detail.gift.get()
            gift.put_in_order()

        # use only gifts_copy, not response_json.get('gifts', [])
        # it is used for creating db for promos
        validate_order(client, order_json['items'], gifts_copy, order_json.get('order_gifts', []),
                       order_json.get('cancelled_order_gifts', []), order_json['payment'],
                       venue, address_json, self.order.delivery_time, delivery_slot, self.order.delivery_type, delivery_zone, False,
                       self.order)

        self.order.status = NEW_ORDER
        self.order.put()

        send_venue_sms(venue, self.order)
        send_venue_email(venue, self.order, self.request.url, self.jinja2)
        send_client_sms(self.order)

        self.response.status_int = 201
        self.render_json({
            'order_id': self.order.key.id(),
            'delivery_time': validation_result['delivery_time'],
            'delivery_slot_name': validation_result['delivery_slot_name']
        })


class RegisterOrderHandler(ApiHandler):
    def get(self):
        self.render_json({'order_id': Order.generate_id()})


class ReturnOrderHandler(ApiHandler):
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        elif order.status != NEW_ORDER:
            self.response.status_int = 412
            self.render_json({
                'error': 1,
                'description': u'Заказ уже выдан или отменен'
            })
        else:
            now = datetime.utcnow()
            if now - order.date_created < timedelta(seconds=config.CANCEL_ALLOWED_WITHIN) or \
                    order.delivery_time - now > timedelta(minutes=config.CANCEL_ALLOWED_BEFORE):
                success = cancel_order(order, CANCELED_BY_CLIENT_ORDER, namespace_manager.get_namespace(),
                                       with_push=False)
                if success:
                    reason_id = self.request.get('reason_id')
                    if reason_id:
                        reason_id = int(reason_id)
                        if reason_id in CONFUSED_CHOICES:
                            order.cancel_reason = reason_id
                        if reason_id == CONFUSED_OTHER:
                            order.cancel_reason_text = self.request.get('reason_text')
                        order.put()
                    self.render_json({
                        'error': 0,
                        'order_id': order.key.id()
                    })
                    logging.info(u'заказ %d отменен' % order_id)
                else:
                    self.response.status_int = 422
                    self.render_json({
                        'error': 1,
                        'description': u'При отмене возникла ошибка'  # todo: change this text
                    })
            else:
                self.response.status_int = 412
                self.render_json({
                    'error': 1,
                    'description': u'Отмена заказа невозможна, так как до его исполнения осталось менее %s минут.' %
                                   config.CANCEL_ALLOWED_BEFORE
                })


#  all required fields should invoke 400
#  all errors should be catch in validate_order
## venue can be None         => send error
## delivery time can be None => send error
## address can be None       => send error
## payment can be None       => send error

## delivery slot can't be None => it violates logic
## client can't be None => it violates logic
class CheckOrderHandler(ApiHandler):
    def post(self):
        logging.info(self.request.POST)

        client_id = self.request.get_range('client_id')
        client = Client.get_by_id(client_id)
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
        if config.APP_KIND == AUTO_APP:
            result = validate_order(client, items, gifts, order_gifts, cancelled_order_gifts, payment_info, venue,
                                    address, delivery_time, delivery_slot, delivery_type, delivery_zone)
        elif config.APP_KIND == RESTO_APP:
            result = resto_validate_order(client, items, venue, delivery_time)
        else:
            result = {}
        self.render_json(result)