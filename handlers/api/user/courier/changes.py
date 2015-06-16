from handlers.api.user.courier.base import CourierBaseHandler
from methods.auth import api_courier_required
from methods.orders.done import done_order
from methods.rendering import timestamp
from models.order import ON_THE_WAY

__author__ = 'dvpermyakov'


class DoneOrderHandler(CourierBaseHandler):
    @api_courier_required
    def post(self, order_id):
        order = self.user.order_by_id(int(order_id))
        if order.status != ON_THE_WAY:
            self.abort(400)
        done_order(order, self.user.namespace)
        self.render_json({
            "success": True,
            "delivery_time": timestamp(order.delivery_time),
            "actual_delivery_time": timestamp(order.actual_delivery_time)
        })