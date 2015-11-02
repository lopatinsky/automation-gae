import datetime
from handlers.api.user.admin.base import AdminApiHandler
from methods.auth import api_admin_required
from methods.rendering import timestamp
from models import Order


class UpdatesHandler(AdminApiHandler):
    @api_admin_required
    def get(self):
        now = datetime.datetime.utcnow()
        timestamp_from = self.request.get_range("timestamp")
        time = datetime.datetime.fromtimestamp(timestamp_from)
        orders = self.user.query_orders(Order.updated >= time).fetch()
        new = [order for order in orders if order.date_created > time]
        updated = [order for order in orders if order.date_created <= time]
        self.render_json({
            "new_orders": [o.dict(extra_fields_in_comment=self._is_android_barista_app) for o in new],
            "updated": [o.dict(extra_fields_in_comment=self._is_android_barista_app) for o in updated],
            "timestamp": timestamp(now)
        })
