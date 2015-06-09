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
    def post(self):
        response_json = json.loads(self.request.get('orders'))
        orders = []
        for order_id in response_json['orders']:
            order = Order.get_by_id(int(order_id))
            if order:
                orders.append(order)
        self.render_json({
            'status': [order.status_dict() for order in orders]
        })