from .base import ApiHandler
from models import Order


class HistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        history = Order.query(Order.client_id == client_id)
        sorted_history = sorted(history, key=lambda order: order.delivery_time, reverse=True)
        self.render_json({
            'orders': [order.history_dict() for order in sorted_history]
        })
