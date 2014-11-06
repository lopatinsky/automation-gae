import datetime
from .base import AdminApiHandler
from methods.auth import api_user_required
from models import Order


class UpdatesHandler(AdminApiHandler):
    @api_user_required
    def get(self):
        timestamp = self.request.get_range("timestamp")
        time = datetime.datetime.fromtimestamp(timestamp)
        orders = self.user.query_orders(Order.updated >= time).fetch()
        new = [order for order in orders if order.date_created > time]
        updated = [order for order in orders if order.date_created <= time]
        self.render_json({
            "new": [o.dict() for o in new],
            "updated": [o.dict() for o in updated]
        })
