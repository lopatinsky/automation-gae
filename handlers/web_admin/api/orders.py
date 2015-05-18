# coding=utf-8

from collections import Counter
import datetime
import logging
from google.appengine.ext import ndb
from .base import WebAdminApiHandler
from methods import push, alfa_bank, empatika_promos, empatika_wallet
from methods.auth import api_user_required
from models import Order, Client, NEW_ORDER, CANCELED_BY_CLIENT_ORDER, READY_ORDER, \
    CANCELED_BY_BARISTA_ORDER, SharedFreeCup, Venue


def format_order(order):
    client = Client.get_by_id(order.client_id)
    order_data = {
        'date_created': order.date_created.strftime("%Y-%m-%d %H:%M:%S"),
        'delivery_time': order.delivery_time.strftime("%H:%M"),
        'comment': order.comment,
        'payment_type_id': order.payment_type_id,
        'order_id': order.key.id(),
        'pan': order.pan,
        'name': client.name,
        'surname': client.surname,
        'tel': client.tel,
        'items': []
    }
    item_keys = Counter(order.items).items()
    for key, count in item_keys:
        item = key.get()
        order_data['items'].append({
            'title': item.title,
            'price': item.price,
            'quantity': count
        })
    return order_data


class CheckTimeHandler(WebAdminApiHandler):
    @api_user_required
    def post(self):
        mins = self.request.get_range("mins")
        order_id = self.request.get_range("order_id")

        order = self.user.order_by_id(order_id)
        order.delivery_time += datetime.timedelta(minutes=mins)
        order.put()

        venue = Venue.get_by_id(order.venue_id)
        local_delivery_time = order.delivery_time + datetime.timedelta(hours=venue.timezone_offset)
        push_time_str = local_delivery_time.strftime("%H:%M")
        client = Client.get_by_id(order.client_id)
        push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order_id, push_time_str)
        push.send_order_push(order_id, order.status, push_text, order.device_type, new_time=order.delivery_time)

        response = {
            'error': 0,
            'info': {
                'time': order.delivery_time.strftime("%H:%M"),
                'order_id': order_id
            }
        }
        self.render_json(response)


class CheckUpdateHandler(WebAdminApiHandler):
    @api_user_required
    def post(self):
        last_date_str = self.request.get("last_order_datetime")
        last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
        orders = self.user.query_orders(Order.date_created > last_date).fetch()
        response = {}
        if orders:
            response['status'] = 1
            response['data'] = {}
            for order in orders:
                if order.status != NEW_ORDER:
                    continue
                response['data'][order.key.id()] = format_order(order)
        else:
            response['status'] = 0
        cancel_keys = self.user.query_orders(Order.status == CANCELED_BY_CLIENT_ORDER).fetch(keys_only=True)
        cancel_ids = [k.id() for k in cancel_keys]
        response['cancel'] = cancel_ids
        self.render_json(response)


class OrderDoneHandler(WebAdminApiHandler):
    @api_user_required
    def post(self):
        order_id = self.request.get_range("order_id")
        order = self.user.order_by_id(order_id)
        order.status = READY_ORDER
        order.actual_delivery_time = datetime.datetime.utcnow()
        order.put()

        order.activate_cash_back()
        order.activate_gift_points()

        client_key = ndb.Key(Client, order.client_id)
        free_cup = SharedFreeCup.query(SharedFreeCup.recipient == client_key,
                                       SharedFreeCup.status == SharedFreeCup.READY).get()
        if free_cup:
            free_cup.deactivate_cup()

        if order.has_card_payment:
            alfa_bank.deposit(order.payment_id, 0)  # TODO check success
        push.send_order_ready_push(order)

        response = {
            'status': 1,
            'error': 0,
            'order_id': order_id
        }
        self.render_json(response)


class OrderCancelHandler(WebAdminApiHandler):
    @api_user_required
    def post(self):
        order_id = self.request.get_range('order_id')
        comment = self.request.get('comment')
        order = self.user.order_by_id(order_id)

        success = True
        if order.has_card_payment:
            return_result = alfa_bank.reverse(order.payment_id)
            success = str(return_result['errorCode']) == '0'
        for gift_detail in order.gift_details:
            try:
                empatika_promos.cancel_activation(gift_detail.activation_id)
            except empatika_promos.EmpatikaPromosError as e:
                logging.exception(e)
                success = False

        if success:
            if order.wallet_payment > 0:
                try:
                    empatika_wallet.reverse(order.client_id, order_id)
                except empatika_wallet.EmpatikaWalletError as e:
                    logging.exception(e)
                    # do not abort -- primary payment reversed

            order.status = CANCELED_BY_BARISTA_ORDER
            order.return_datetime = datetime.datetime.utcnow()
            order.return_comment = comment
            order.put()

            client = Client.get_by_id(order.client_id)
            push_text = u"%s, заказ №%s отменен." % (client.name, order_id)
            if order.has_card_payment:
                push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут."
            push.send_order_push(order_id, order.status, push_text, order.device_type)

            response = {
                'error': 0,
                'order_id': order_id
            }
        else:
            response = {
                'error': 1,
                'error_descr': 'Alfabank error'
            }
        self.render_json(response)


class OrderStatusUpdateHandler(WebAdminApiHandler):
    @api_user_required
    def post(self):
        order_id = self.request.get_range("order_id")
        status = self.request.get_range("status")
        order = self.user.order_by_id(order_id)
        order.status = status
        order.put()
        self.render_json({
            'error': 0,
            'order_id': order_id,
            'status': status
        })
