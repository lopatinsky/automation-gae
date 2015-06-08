# coding=utf-8
import datetime
from .base import BaseHandler
from .formatting import format_order
from methods.auth import user_required
from methods.orders import search_orders
from models import Order
from models.order import STATUS_MAP
from models.payment_types import PAYMENT_TYPE_MAP


class HistoryHandler(BaseHandler):
    @user_required
    def get(self):
        search_string = self.request.get("search")
        if search_string:
            orders = search_orders(search_string, self.user)
        else:
            today = datetime.datetime.combine(datetime.date.today(), datetime.time())
            orders = self.user.query_orders(Order.date_created >= today).order(-Order.date_created).fetch()
        orders_data = []
        total_price = 0
        total_cost_price = 0
        for order in orders:
            order_data = format_order(order)
            orders_data.append(order_data)
            total_price += order.total_sum
            for item in order_data['items']:
                total_cost_price += item['cost_price']

        status_strings = STATUS_MAP
        payment_type_strings = PAYMENT_TYPE_MAP

        self.render('history.html', orders=orders_data, status_strings=status_strings,
                    payment_type_strings=payment_type_strings)
