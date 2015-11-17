from handlers.api.base import ApiHandler
from models.client import Client
from models.order import OrderRate, Order

__author__ = 'dvpermyakov'


class OrderReviewHandler(ApiHandler):
    def post(self):
        client_id = int(self.request.headers.get('Client-Id') or 0)
        client = Client.get(client_id)
        if not client:
            self.abort(400)
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if order.client_id != client.key.id():
            self.abort(409)
        meal_rate = float(self.request.get('meal_rate'))
        service_rate = float(self.request.get('service_rate'))
        comment = self.request.get('comment')
        rate = OrderRate(meal_rate=meal_rate, service_rate=service_rate, comment=comment)
        order.rate = rate
        order.put()
        self.render_json({})
