from .base import ApiHandler
from models import Order, CASH_PAYMENT_TYPE, BONUS_PAYMENT_TYPE, CREATING_ORDER


class HistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        history = Order.query(Order.client_id == client_id)
        sorted_history = sorted(history, key=lambda order: order.delivery_time, reverse=True)

        order_dicts = [order.history_dict() for order in sorted_history if order.status != CREATING_ORDER]

        # fuckup iOS v1.2
        ua = self.request.headers["User-Agent"]
        if "/1.2 " in ua and "Android" not in ua:
            for order_dict in order_dicts:
                if order_dict["payment_type_id"] == BONUS_PAYMENT_TYPE:
                    order_dict["payment_type_id"] = CASH_PAYMENT_TYPE
        # fuckup end

        self.render_json({
            'orders': order_dicts
        })
