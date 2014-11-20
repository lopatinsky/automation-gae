import datetime
from .base import AdminApiHandler
from methods.auth import api_user_required
from methods.orders import search_orders
from models import Order, NEW_ORDER, CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER


class OrderListBaseHandler(AdminApiHandler):
    def _get_orders(self):
        return []

    @api_user_required
    def get(self):
        orders = self._get_orders()
        self.render_json({'orders': [order.dict() for order in orders]})


class CurrentOrdersHandler(OrderListBaseHandler):
    def _get_orders(self):
        now = datetime.datetime.now()
        today = datetime.datetime.combine(now.date(), datetime.time())
        orders = self.user.query_orders(Order.date_created >= today,
                                        Order.status == NEW_ORDER) \
                          .order(-Order.date_created).fetch()
        return [o for o in orders if o.status == NEW_ORDER or o.delivery_time >= now]


class ReturnsHandler(OrderListBaseHandler):
    def _get_orders(self):
        timestamp = self.request.get_range("date")
        if timestamp:
            date = datetime.date.fromtimestamp(timestamp)
            date = datetime.datetime.combine(date, datetime.time())
        else:
            date = datetime.datetime.combine(datetime.date.today(), datetime.time())
        next_date = date + datetime.timedelta(days=1)
        orders = self.user.query_orders(Order.status.IN((CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER)),
                                        Order.date_created >= date, Order.date_created < next_date).fetch()
        return orders


class HistoryHandler(OrderListBaseHandler):
    def _get_orders(self):
        start_timestamp = self.request.get_range("start")
        end_timestamp = self.request.get_range("end")
        if not start_timestamp or not end_timestamp:
            self.abort(400)
        start = datetime.datetime.fromtimestamp(start_timestamp)
        end = datetime.datetime.fromtimestamp(end_timestamp)
        search = self.request.get("search").strip()
        if search:
            return search_orders(search, self.user, start, end)
        else:
            return self.user.query_orders(Order.date_created >= start, Order.date_created < end).fetch()
