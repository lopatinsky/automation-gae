import datetime
from handlers.api.user.courier.base import CourierBaseHandler
from methods.auth import api_courier_required
from methods.rendering import timestamp
from models.order import CREATING_ORDER, Order, ON_THE_WAY

__author__ = 'dvpermyakov'


class OrderListBaseHandler(CourierBaseHandler):
    _with_timestamp = False

    def _get_orders(self):
        return []

    @api_courier_required
    def get(self):
        orders = self._get_orders()
        dct = {'orders': [order.dict() for order in orders if order.status != CREATING_ORDER]}
        if self._with_timestamp:
            dct['timestamp'] = timestamp(datetime.datetime.utcnow())
        self.render_json(dct)


class CurrentOrdersHandler(OrderListBaseHandler):
    _with_timestamp = True

    def _get_orders(self):
        return self.user.query_orders()


class HistoryHandler(OrderListBaseHandler):
    def _get_orders(self):
        start_timestamp = self.request.get_range("start")
        end_timestamp = self.request.get_range("end")
        if not start_timestamp or not end_timestamp:
            self.abort(400)
        start = datetime.datetime.fromtimestamp(start_timestamp)
        end = datetime.datetime.fromtimestamp(end_timestamp)
        return self.user.query_orders(Order.date_created >= start, Order.date_created < end).fetch()