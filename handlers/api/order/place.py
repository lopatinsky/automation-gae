# coding=utf-8
import copy
import logging
import json
from google.appengine.api import memcache

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from google.appengine.ext.ndb import GeoPt

from models.config.config import config, RESTO_APP
from handlers.api.base import ApiHandler
from methods import empatika_promos, empatika_wallet
from methods.orders.create import send_venue_sms, send_venue_email, send_client_sms_task, card_payment_performing, \
    paypal_payment_performing, set_address_obj, send_demo_sms
from methods.orders.validation.validation import validate_order
from methods.orders.validation.precheck import get_order_id, set_client_info, get_venue_and_zone_by_address,\
    check_items_and_gifts, get_delivery_time, validate_address, check_after_error, after_validation_check, \
    set_extra_order_info
from methods.proxy.resto.place_order import resto_place_order
from methods.subscription import get_subscription
from methods.subscription import get_amount_of_subscription_items
from models import DeliverySlot, PaymentType, Order, Venue, STATUS_UNAVAILABLE, STATUS_AVAILABLE
from models.client import IOS_DEVICE
from models.config.version import CURRENT_APP_ID, DEMO_APP_ID
from models.order import NEW_ORDER, CREATING_ORDER, SubscriptionDetails
from models.payment_types import CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE
from models.venue import SELF, IN_CAFE, DELIVERY, PICKUP

__author__ = 'dvpermyakov'


class OrderHandler(ApiHandler):
    order = None
    cache_key = None

    def render_error(self, description):
        if self.order:
            self.order.key.delete()
        if self.cache_key:
            memcache.delete(self.cache_key)
        self.response.set_status(400)
        logging.warning('error: %s' % description)
        self.render_json({
            'title': u'Ошибка',
            'description': description
        })

    def post(self):
        if config.BLOCK_ORDER:
            return self.render_error(u'К сожалению, компания больше не принимает заказы через мобильное приложение')

        order_json = json.loads(self.request.get('order'))

        order_id, self.cache_key = get_order_id(order_json)
        if not order_id:
            self.abort(409)
        self.order = Order(id=order_id, unified_app_namespace=self.request.init_namespace)
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
                return self.render_error(u"Произошла ошибка. Попробуйте заново выбрать точку.")
            venue = Venue.get(venue_id)
            if not venue:
                return self.render_error(u"Кофейня не найдена")
        elif self.order.delivery_type in [DELIVERY]:
            if address_json:
                address_json = validate_address(address_json)
                venue, delivery_zone = get_venue_and_zone_by_address(address_json)
        self.order.venue_id = str(venue.key.id())

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

        client = set_client_info(order_json.get('client'), self.request.headers)
        if not client:
            return self.render_error(u'Неудачная попытка авторизации. Попробуйте позже')
        self.order.client_id = client.key.id()
        self.order.user_agent = self.request.headers["User-Agent"]

        self.order.payment_type_id = order_json['payment']['type_id']
        payment_type = PaymentType.get(self.order.payment_type_id)
        if payment_type.status == STATUS_UNAVAILABLE:
            return self.render_error(u"Выбранный способ оплаты недоступен.")

        self.order.wallet_payment = order_json['payment'].get('wallet_payment', 0)

        # todo: it can be checked in validation
        extra_fields = order_json.get('extra_order_field', {})
        if not extra_fields:
            try:
                extra_fields = json.loads(self.request.get('extra_order_field'))
            except:
                pass
        set_extra_order_info(self.order, extra_fields)

        if check_after_error(order_json, client):
            return self.render_error(u"Этот заказ уже зарегистрирован в системе, проверьте историю заказов.")

        if config.APP_KIND == RESTO_APP:
            success, response = resto_place_order(client, venue, self.order, order_json['payment'], order_json['items'],
                                                  order_json.get('order_gifts', []),
                                                  order_json.get('cancelled_order_gifts', []))
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

        subscription = get_subscription(client)
        if subscription:
            amount = get_amount_of_subscription_items(order_json['items'])
        else:
            amount = 0
        if subscription and amount:
            success = subscription.deduct(amount)
            if success:
                self.order.subscription_details = SubscriptionDetails(subscription=subscription.key, amount=amount)
            else:
                return self.render_json(u'Не удалось произвести покупку по абонементу')

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
        send_venue_email(venue, self.order, self.request.host_url, self.jinja2)
        send_client_sms_task(self.order, namespace_manager.get_namespace())
        if CURRENT_APP_ID == DEMO_APP_ID:
            send_demo_sms(client)

        show_share = False
        if config.SHARE_INVITATION_MODULE and config.SHARE_INVITATION_MODULE.status == STATUS_AVAILABLE:
            show_share = True  # todo this is for test only

        self.response.status_int = 201
        self.render_json({
            'order_id': self.order.key.id(),
            'number': self.order.number,
            'delivery_time': validation_result['delivery_time'],
            'delivery_slot_name': validation_result['delivery_slot_name'],
            'show_share': show_share,
        })
