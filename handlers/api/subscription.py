# coding=utf-8
import json
import logging
from handlers.api.base import ApiHandler
from methods.orders.create import card_payment_performing, paypal_payment_performing
from datetime import datetime, timedelta
from methods.rendering import timestamp
from methods.subscription import get_subscription, get_subscription_category_dict
from models import Order, Client, Venue, STATUS_AVAILABLE, STATUS_UNAVAILABLE
from models.payment_types import CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE
from models.subscription import SubscriptionMenuItem, SubscriptionTariff, Subscription
from models.config.config import config

__author__ = 'dvpermyakov'


class SubscriptionInfoHandler(ApiHandler):
    def get(self):
        client_id = self.request.headers.get('Client-Id', 0)
        if not client_id:
            self.abort(400)
        client = Client.get(int(client_id))

        enabled, category_dict = get_subscription_category_dict()
        if not enabled:
            self.abort(400)
        dct = {
            "category": category_dict
        }

        subscription = get_subscription(client)
        if subscription:
            dct.update(subscription.dict())
        self.render_json(dct)


class SubscriptionTariffsHandler(ApiHandler):
    def get(self):
        tariffs = SubscriptionTariff.query(SubscriptionTariff.status == STATUS_AVAILABLE).fetch()
        self.render_json({
            'tariffs': [tariff.dict() for tariff in tariffs]
        })


class BuySubscriptionHandler(ApiHandler):
    def render_error(self, description):
        self.response.set_status(400)
        logging.warning('error: %s' % description)
        self.render_json({
            'success': False,
            'description': description
        })

    def post(self):
        client_id = self.request.headers.get('Client-Id', 0)
        if not client_id:
            self.abort(400)
        client = Client.get(int(client_id))
        tariff_id = self.request.get_range('tariff_id')
        if not tariff_id:
            return self.render_error(u'Тариф не найден')
        tariff = SubscriptionTariff.get_by_id(int(tariff_id))
        if tariff.status == STATUS_UNAVAILABLE:
            return self.render_error(u'Тариф не доступен')
        subscription = get_subscription(client)
        if subscription:
            if subscription.used_cups < subscription.initial_amount:
                return self.render_error(u'Ваш текущий абонемент еще не использован')
            else:
                return self.render_error(u"Срок действия текущего абонемента еще не истек")
        payment_json = json.loads(self.request.get('payment'))
        order_id = 'subscription_%s_%s' % (client.key.id(), timestamp(datetime.utcnow()))
        order = Order(id=order_id)
        order.payment_type_id = payment_json['type_id']
        if config.SUBSCRIPTION_MODULE.legal_for_payment:
            legal = config.SUBSCRIPTION_MODULE.legal_for_payment
            venue = Venue.query(Venue.legal == legal).get()
        else:
            venue = Venue.query().get()
            legal = venue.legal
        order.venue_id = str(venue.key.id())
        if order.payment_type_id == CARD_PAYMENT_TYPE:
            success, result = card_payment_performing(payment_json, tariff.price * 100, order,
                                                     put_order=False)
            if not success:
                return self.render_error(result)
            else:
                payment_id = result
        elif order.payment_type_id == order.payment_type_id == PAYPAL_PAYMENT_TYPE:
            success, result = paypal_payment_performing(payment_json, tariff.price * 100, order, client, put_order=False)
            if not success:
                return self.render_error(result)
            else:
                payment_id = result
        else:
            return self.render_error(u'Возможна оплата только картой')

        seconds_to_return = min(7 * 24 * 3600, tariff.duration_seconds)
        return_time = datetime.utcnow() + timedelta(seconds=seconds_to_return)

        expiration = datetime.utcnow() + timedelta(seconds=tariff.duration_seconds)
        subscription = Subscription(
                client=client.key, tariff=tariff.key, initial_amount=tariff.amount,  expiration=expiration,
                payment_id=payment_id, payment_type_id=order.payment_type_id, payment_amount=tariff.price,
                payment_legal=legal, payment_return_time=return_time)
        subscription.put()
        subscription_dict = subscription.dict()
        subscription_dict.update({
            'items': [item.dict()
                      for item in SubscriptionMenuItem.query(SubscriptionMenuItem.status == STATUS_AVAILABLE).fetch()]
        })
        self.render_json({
            'success': True,
            'subscription': subscription_dict
        })
