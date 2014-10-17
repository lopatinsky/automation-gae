import datetime
from .base import AdminApiHandler
from models import Order


class UpdatesHandler(AdminApiHandler):
    def get(self):
        timestamp = self.request.get_range("timestamp")
        time = datetime.datetime.fromtimestamp(timestamp)
        orders = Order.query(Order.updated >= time).fetch()
        new = [order for order in orders if order.date_created > timestamp]
        updated = [order for order in orders if order.date_created <= timestamp]
        self.render_json({
            "new": [o.dict() for o in new],
            "updated": [o.dict() for o in updated]
        })
