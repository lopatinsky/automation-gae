# coding=utf-8
import json
import logging
from handlers.api.base import ApiHandler
from methods.orders.create import card_payment_performing, paypal_payment_performing
from datetime import datetime, timedelta
from methods.rendering import timestamp
from methods.subscription import get_subscription
from models import Order, Client, Venue, STATUS_AVAILABLE, STATUS_UNAVAILABLE
from models.payment_types import CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE
from models.specials import SubscriptionTariff, Subscription, SubscriptionMenuItem

__author__ = 'dvpermyakov'


class SubscriptionInfoHandler(ApiHandler):
    def get(self):
        client_id = self.request.headers.get('Client-Id', 0)
        if not client_id:
            self.abort(400)
        client = Client.get_by_id(int(client_id))
        subscription = get_subscription(client)
        if subscription:
            subscription_dict = subscription.dict()
            subscription_dict.update(SubscriptionMenuItem.get().dict())
            self.render_json(subscription_dict)
        else:
            self.render_json({})


class SubscriptionTariffsHandler(ApiHandler):
    def get(self):
        tariffs = SubscriptionTariff.query(SubscriptionTariff.status == STATUS_AVAILABLE).fetch()
        self.render_json({
            'tariffs': [tariff.dict() for tariff in tariffs]
        })


class BuySubscriptionHandler(ApiHandler):
    LAST_BUYING_SECONDS = 10

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
        client = Client.get_by_id(int(client_id))
        tariff_id = self.request.get_range('tariff_id')
        if not tariff_id:
            return self.render_error(u'Тариф не найден')
        tariff = SubscriptionTariff.get_by_id(int(tariff_id))
        if tariff.status == STATUS_UNAVAILABLE:
            return self.render_error(u'Тариф не доступен')
        subscription = get_subscription(client)
        if subscription and (datetime.utcnow() - subscription.updated).seconds < self.LAST_BUYING_SECONDS:
            return self.render_error(u'Вы уже совершили покупку')
        payment_json = json.loads(self.request.get('payment'))
        order_id = 'subscription_%s_%s' % (client.key.id(), timestamp(datetime.utcnow()))
        order = Order(id=order_id)
        order.payment_type_id = payment_json['type_id']
        order.venue_id = str(Venue.query(Venue.active == True).get().key.id())
        if order.payment_type_id == CARD_PAYMENT_TYPE:
            success, error = card_payment_performing(payment_json, tariff.price, order,
                                                     put_order=False)
            if not success:
                return self.render_error(error)
        elif order.payment_type_id == order.payment_type_id == PAYPAL_PAYMENT_TYPE:
            success, error = paypal_payment_performing(payment_json, tariff.price, order, client, put_order=False)
            if not success:
                return self.render_error(error)
        else:
            return self.render_error(u'Возможна оплата только картой')
        expiration = datetime.utcnow() + timedelta(seconds=tariff.duration_seconds)
        if subscription:
            subscription.rest += tariff.amount
            subscription.expiration = expiration
            subscription.tariff = tariff.key
            subscription.put()
        else:
            subscription = Subscription(client=client.key, tariff=tariff.key, rest=tariff.amount, expiration=expiration)
            subscription.put()
        subscription_dict = subscription.dict()
        subscription_dict.update(SubscriptionMenuItem.get().dict())
        self.render_json({
            'success': True,
            'subscription': subscription_dict
        })
