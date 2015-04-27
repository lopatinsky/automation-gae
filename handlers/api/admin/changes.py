# coding=utf-8
import datetime
import logging
from google.appengine.ext import ndb
from handlers.api.admin.base import AdminApiHandler
from methods import push, alfa_bank, empatika_promos, empatika_wallet
from methods.auth import write_access_required
from methods.rendering import timestamp
from models import CARD_PAYMENT_TYPE, CANCELED_BY_BARISTA_ORDER, Client, READY_ORDER, BONUS_PAYMENT_TYPE, \
    NEW_ORDER, SharedFreeCup, Venue

__author__ = 'ilyazorin'


class CancelOrderHandler(AdminApiHandler):
    @write_access_required
    def post(self, order_id):
        comment = self.request.get('comment')
        order = self.user.order_by_id(int(order_id))

        success = True
        if order.payment_type_id == CARD_PAYMENT_TYPE:
            return_result = alfa_bank.reverse(order.payment_id)
            success = str(return_result['errorCode']) == '0'
        elif order.payment_type_id == BONUS_PAYMENT_TYPE:
            try:
                empatika_promos.cancel_activation(order.payment_id)
            except empatika_promos.EmpatikaPromosError as e:
                logging.exception(e)
                success = False

        if order.wallet_payment > 0:
            try:
                empatika_wallet.reverse(order.client_id, order_id)
            except empatika_wallet.EmpatikaWalletError as e:
                logging.exception(e)
                success = False

        if success:
            order.status = CANCELED_BY_BARISTA_ORDER
            order.return_datetime = datetime.datetime.utcnow()
            order.return_comment = comment
            order.put()

            client = Client.get_by_id(order.client_id)
            push_text = u"%s, заказ №%s отменен." % (client.name, order_id)
            if order.payment_type_id == CARD_PAYMENT_TYPE:
                push_text += u" Ваш платеж будет возвращен на карту в течение нескольких минут.\n"
                push_text += comment
            push.send_order_push(order_id, order.status, push_text, order.device_type)

            self.render_json({})
        else:
            self.response.status_int = 400
            self.render_json({})


class DoneOrderHandler(AdminApiHandler):
    @write_access_required
    def post(self, order_id):
        order = self.user.order_by_id(int(order_id))
        if order.status != NEW_ORDER:
            self.abort(400)

        order.activate_cash_back()

        order.status = READY_ORDER
        order.actual_delivery_time = datetime.datetime.utcnow()
        order.put()

        client_key = ndb.Key(Client, order.client_id)
        free_cup = SharedFreeCup.query(SharedFreeCup.recipient == client_key,
                                       SharedFreeCup.status == SharedFreeCup.READY).get()
        if free_cup:
            free_cup.deactivate_cup()

        if order.payment_type_id == CARD_PAYMENT_TYPE:
            alfa_bank.deposit(order.payment_id, 0)  # TODO check success
        push.send_order_ready_push(order)

        self.render_json({
            "delivery_time": timestamp(order.delivery_time),
            "actual_delivery_time": timestamp(order.actual_delivery_time)
        })


class PostponeOrderHandler(AdminApiHandler):
    @write_access_required
    def post(self, order_id):
        mins = self.request.get_range("mins")

        order = self.user.order_by_id(int(order_id))
        order.delivery_time += datetime.timedelta(minutes=mins)
        order.put()

        venue = Venue.get_by_id(order.venue_id)
        local_delivery_time = order.delivery_time + datetime.timedelta(hours=venue.timezone_offset)
        time_str = local_delivery_time.strftime("%H:%M")
        client = Client.get_by_id(order.client_id)
        push_text = u"%s, готовность заказа №%s была изменена на %s" % (client.name, order_id, time_str)
        push.send_order_push(order_id, order.status, push_text, order.device_type, new_time=order.delivery_time)

        self.render_json({})
