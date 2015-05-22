# coding=utf-8
from handlers.api.admin.base import AdminApiHandler
from methods.orders.cancel import cancel_order
from methods.orders.done import done_order
from methods.orders.postpone import postpone_order
from methods.auth import write_access_required
from methods.rendering import timestamp
from models import CANCELED_BY_BARISTA_ORDER, NEW_ORDER

__author__ = 'ilyazorin'


class CancelOrderHandler(AdminApiHandler):
    @write_access_required
    def post(self, order_id):
        comment = self.request.get('comment')
        order = self.user.order_by_id(int(order_id))
        success = cancel_order(order, CANCELED_BY_BARISTA_ORDER, comment)
        if not success:
            self.response.status_int = 400
        self.render_json({})


class DoneOrderHandler(AdminApiHandler):
    @write_access_required
    def post(self, order_id):
        order = self.user.order_by_id(int(order_id))
        if order.status != NEW_ORDER:
            self.abort(400)
        done_order(order)
        self.render_json({
            "delivery_time": timestamp(order.delivery_time),
            "actual_delivery_time": timestamp(order.actual_delivery_time)
        })


class PostponeOrderHandler(AdminApiHandler):
    @write_access_required
    def post(self, order_id):
        mins = self.request.get_range("mins")
        order = self.user.order_by_id(int(order_id))
        postpone_order(order, mins)
        self.render_json({})
