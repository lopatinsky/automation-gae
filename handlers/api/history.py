from .base import ApiHandler
from methods import versions
from models import Order, CASH_PAYMENT_TYPE, BONUS_PAYMENT_TYPE, CREATING_ORDER, IOS_DEVICE


class HistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id')
        history = Order.query(Order.client_id == client_id)
        sorted_history = sorted(history, key=lambda order: order.delivery_time, reverse=True)

        order_dicts = [order.history_dict() for order in sorted_history if order.status != CREATING_ORDER]

        # fuckup iOS v1.2
        platform_and_version = versions.get_platform_and_version(self.request)
        if platform_and_version == (IOS_DEVICE, 10200):
            for order_dict in order_dicts:
                if order_dict["payment_type_id"] == BONUS_PAYMENT_TYPE:
                    order_dict["payment_type_id"] = CASH_PAYMENT_TYPE
        # fuckup end

        self.render_json({
            'orders': order_dicts
        })
