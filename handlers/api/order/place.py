# coding=utf-8
import copy
import json
import logging

from google.appengine.api import memcache, taskqueue
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from google.appengine.ext.ndb import GeoPt

from handlers.api.base import ApiHandler
from methods import empatika_promos, empatika_wallet
from methods.fuckups import fuckup_move_items_to_gifts
from methods.orders.create import send_venue_sms, send_venue_email, send_client_sms_task, card_payment_performing, \
    paypal_payment_performing, set_address_obj, send_demo_sms, need_to_show_share_invitation
from methods.orders.validation.precheck import get_order_id, set_client_info, get_venue_and_zone_by_address, \
    check_items_and_gifts, get_delivery_time, validate_address, check_after_error, after_validation_check, \
    set_extra_order_info
from methods.orders.validation.validation import validate_order
from methods.proxy.doubleb.place_order import doubleb_place_order
from methods.proxy.resto.place_order import resto_place_order
from methods.subscription import get_amount_of_subscription_items
from methods.subscription import get_subscription
from models import DeliverySlot, PaymentType, Order, Venue, STATUS_UNAVAILABLE, STATUS_AVAILABLE
from models.client import IOS_DEVICE
from models.config.config import config, RESTO_APP, COMPANY_REMOVED, COMPANY_PREVIEW, DOUBLEB_APP
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
        if config.COMPANY_STATUS == COMPANY_REMOVED:
            return self.render_error(u'К сожалению, компания больше не принимает заказы через мобильное приложение')
        elif config.COMPANY_STATUS == COMPANY_PREVIEW:
            return self.render_error(u'К сожалению, компания пока не принимает заказы через мобильное приложение')

        order_json = json.loads(self.request.get('order'))

        order_id, self.cache_key = get_order_id(order_json)
        if not order_id:
            self.abort(409)
        self.order = Order(id=order_id, unified_app_namespace=self.request.init_namespace)
        self.order.version = int(self.request.headers.get('Version', 0))
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
        if delivery_zone:
            self.order.delivery_zone = delivery_zone.key
        self.order.venue_id = str(venue.key.id())

        if address_json:
            set_address_obj(address_json, self.order)

        coordinates = order_json.get('coordinates')
        if coordinates:
            self.order.coordinates = GeoPt(coordinates)

        self.order.comment = order_json['comment']
        self.order.device_type = order_json.get('device_type', IOS_DEVICE)

        if config.SMS_CONFIRMATION_MODULE and config.SMS_CONFIRMATION_MODULE.status == STATUS_AVAILABLE:
            confirm_by_sms = order_json.get('confirm_by_sms')
            if confirm_by_sms:
                self.order.comment = u"Клиенту нужно отправить СМС-подтверждение. " + self.order.comment
            else:
                self.order.comment = u"Клиент просит перезвонить. " + self.order.comment


        self.order.delivery_slot_id = int(order_json.get('delivery_slot_id')) \
            if order_json.get('delivery_slot_id') else None
        if self.order.delivery_slot_id > 0:
            delivery_slot = DeliverySlot.get_by_id(self.order.delivery_slot_id)
            if not delivery_slot:
                return self.render_error(u'Неправильный формат времени')
        else:
            delivery_slot = None

        delivery_time_minutes = order_json.get('delivery_time')  # used for old versions todo: remove
        if delivery_time_minutes:  # used for old versions todo: remove
            delivery_time_minutes = int(delivery_time_minutes)  # used for old versions todo: remove
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
        num_people = order_json.get('num_people')
        cash_change = order_json.get('cash_change')
        set_extra_order_info(self.order, extra_fields, num_people, cash_change)

        if check_after_error(order_json, client):
            return self.render_error(u"Этот заказ уже зарегистрирован в системе, проверьте историю заказов.")

        conf = config
        if conf.ORDER_MESSAGE_MODULE:
            message = conf.ORDER_MESSAGE_MODULE.get_message(self.order)
        else:
            message = u'Заказ отправлен'

        if config.APP_KIND == RESTO_APP:
            success, response = resto_place_order(client, venue, self.order, order_json['payment'], order_json['items'],
                                                  order_json.get('order_gifts', []),
                                                  order_json.get('cancelled_order_gifts', []))
            if success:
                response['message'] = message
                send_client_sms_task(self.order, namespace_manager.get_namespace())
                return self.render_json(response)
            else:
                return self.render_error(response['description'])

        if config.APP_KIND == DOUBLEB_APP:
            success, response = doubleb_place_order(self.order, client, venue, order_json['items'],
                                                    order_json['payment'])
            if success:
                response['message'] = message
                send_client_sms_task(self.order, namespace_manager.get_namespace())
                return self.render_json(response)
            else:
                return self.render_error(response['description'])

        items = order_json['items']
        gifts = order_json.get('gifts', [])

        # todo убрать через ~2 месяца - в июне
        items, gifts = fuckup_move_items_to_gifts(items, gifts)

        # it is need, because item_id and gift_id are swapping
        gifts_copy = copy.deepcopy(gifts)

        validation_result = validate_order(client,
                                           items,
                                           gifts,
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

        self.order.promos = [ndb.Key('Promo', promo['id']) for promo in validation_result["promos"]]
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
            amount = get_amount_of_subscription_items(items)
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
        validate_order(client, items, gifts_copy, order_json.get('order_gifts', []),
                       order_json.get('cancelled_order_gifts', []), order_json['payment'],
                       venue, address_json, self.order.delivery_time, delivery_slot, self.order.delivery_type,
                       delivery_zone, False,
                       self.order)

        self.order.status = NEW_ORDER
        self.order.put()

        send_venue_sms(venue, self.order)
        send_venue_email(venue, self.order, self.request.host_url, self.jinja2,
                         format_type=config.ORDER_EMAIL_FORMAT_TYPE)
        if config.SUSHINSON_EMAIL_MODULE and config.SUSHINSON_EMAIL_MODULE.status == STATUS_AVAILABLE:
            config.SUSHINSON_EMAIL_MODULE.send(self.order, self.jinja2)
        send_client_sms_task(self.order, namespace_manager.get_namespace())
        if CURRENT_APP_ID == DEMO_APP_ID:
            send_demo_sms(client)
        if config.BITRIX_EXT_API_MODULE and config.BITRIX_EXT_API_MODULE.status == STATUS_AVAILABLE:
            taskqueue.add(url=self.uri_for('bitrix_export_task'), params={'order_id': order_id})

        self.response.status_int = 201

        self.render_json({
            'order_id': self.order.key.id(),
            'number': self.order.number,
            'delivery_time': validation_result['delivery_time'],
            'delivery_slot_name': validation_result['delivery_slot_name'],
            'show_share': need_to_show_share_invitation(client),
            'message': message
        })
