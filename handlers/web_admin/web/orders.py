import datetime
from .base import BaseHandler
from .formatting import format_order
from methods.auth import user_required
from models import Order, NEW_ORDER, CANCELED_BY_CLIENT_ORDER


class OrdersHandler(BaseHandler):
    @user_required
    def get(self):
        now = datetime.datetime.now()
        today = datetime.datetime.combine(now.date(), datetime.time())
        orders = self.user.query_orders(Order.date_created >= today,
                                        Order.status == NEW_ORDER or Order.status == CANCELED_BY_CLIENT_ORDER).fetch()
        orders = sorted(orders, key=lambda order: order.delivery_time)
        orders_data = []
        for order in orders:
            if order.status == CANCELED_BY_CLIENT_ORDER and order.delivery_time < now:
                continue

            orders_data.append(format_order(order))

        last_order = self.user.query_orders().order(-Order.date_created).get(projection=(Order.date_created,))
        last_order_datetime = last_order.date_created if last_order else now

        self.render('orders.html', orders=orders_data, last_order_datetime=last_order_datetime)
