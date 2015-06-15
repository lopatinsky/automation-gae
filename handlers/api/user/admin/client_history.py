from handlers.api.user.admin.base import AdminApiHandler
from methods.auth import api_admin_required
from models import Order
from models.order import CREATING_ORDER


class ClientHistoryHandler(AdminApiHandler):
    @api_admin_required
    def get(self, client_id):
        history = Order.query(Order.client_id == int(client_id))
        sorted_history = sorted(history, key=lambda order: order.delivery_time, reverse=True)

        order_dicts = [order.dict() for order in sorted_history if order.status != CREATING_ORDER]

        self.render_json({
            'orders': order_dicts
        })
