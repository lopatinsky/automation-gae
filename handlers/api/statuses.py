import json
from handlers.api.base import ApiHandler
from models import Order

__author__ = 'dvpermyakov'


class ClientSettingSuccessHandler(ApiHandler):
    def post(self):
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        order.response_success = True
        order.put()
        self.render_json({})


class StatusHandler(ApiHandler):
    def get(self):
        order_id = int(self.request.get("order_id"))
        order = Order.get_by_id(order_id)
        dct = order.dict() if order else None
        self.render_json({"order": dct})
