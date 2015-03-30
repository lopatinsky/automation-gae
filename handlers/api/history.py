from .base import ApiHandler
from models import Order, CREATING_ORDER


class HistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        history = Order.query(Order.client_id == client_id)
        sorted_history = sorted(history, key=lambda order: order.delivery_time, reverse=True)

        order_dicts = [order.history_dict() for order in sorted_history if order.status != CREATING_ORDER]

        import logging
        logging.info(order_dicts)

        self.render_json({
            'orders': order_dicts
        })