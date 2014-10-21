# coding=utf-8
import datetime
from .base import BaseHandler
from .formatting import format_order
from methods.orders import search_orders
from models import Order, NEW_ORDER, READY_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER, CARD_PAYMENT_TYPE, \
    CASH_PAYMENT_TYPE


class HistoryHandler(BaseHandler):
    def get(self):
        search_string = self.request.get("search")
        if search_string:
            orders = search_orders(search_string)
        else:
            today = datetime.datetime.combine(datetime.date.today(), datetime.time())
            orders = Order.query(Order.date_created >= today).order(-Order.date_created).fetch()
        orders_data = []
        total_price = 0
        total_cost_price = 0
        for order in orders:
            order_data = format_order(order)
            orders_data.append(order_data)
            total_price += order.total_sum
            for item in order_data['items']:
                total_cost_price += item['cost_price']

        status_strings = {
            NEW_ORDER: u"Новый заказ",
            READY_ORDER: u"Выдано",
            CANCELED_BY_CLIENT_ORDER: u"Отменено клиентом",
            CANCELED_BY_BARISTA_ORDER: u"Отменено баристой"
        }
        payment_type_strings = {
            CARD_PAYMENT_TYPE: u"Карта",
            CASH_PAYMENT_TYPE: u"Наличными"
        }

        self.render('history.html', orders=orders_data, status_strings=status_strings,
                    payment_type_strings=payment_type_strings)
