import datetime
from .base import BaseHandler
from .methods import format_order
from models import Order, NEW_ORDER, CANCELED_BY_CLIENT_ORDER


class OrdersHandler(BaseHandler):
    def get(self):
        now = datetime.datetime.now()
        today = datetime.datetime.combine(now.date(), datetime.time())
        orders = Order.query(Order.date_created >= today,
                             Order.status == NEW_ORDER or Order.status == CANCELED_BY_CLIENT_ORDER) \
                      .order(-Order.date_created).fetch()
        orders_data = []
        for order in orders:
            if order.status == CANCELED_BY_CLIENT_ORDER and order.delivery_time < now:
                continue

            orders_data.append(format_order(order))

        last_order = Order.query().order(-Order.date_created).get(projection=(Order.date_created,))
        last_order_datetime = last_order.date_created if last_order else now

        self.render('orders.html', orders=orders_data, last_order_datetime=last_order_datetime)
