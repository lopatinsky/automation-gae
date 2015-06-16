from datetime import datetime
from handlers.api.user.courier.base import CourierBaseHandler
from methods.auth import api_courier_required
from methods.rendering import timestamp
from models import Order

__author__ = 'dvpermyakov'


class UpdatesHandler(CourierBaseHandler):
    @api_courier_required
    def get(self):
        now = datetime.utcnow()
        timestamp_from = self.request.get_range("timestamp")
        time = datetime.datetime.fromtimestamp(timestamp_from)
        orders = self.user.query_orders(Order.updated >= time).fetch()
        new = [order for order in orders if order.date_created > time]
        updated = [order for order in orders if order.date_created <= time]
        self.render_json({
            "new_orders": [o.dict() for o in new],
            "updated_orders": [o.dict() for o in updated],
            "timestamp": timestamp(now)
        })