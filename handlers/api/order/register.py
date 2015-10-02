from handlers.api.base import ApiHandler
from models import Order

__author__ = 'dvpermyakov'


class RegisterOrderHandler(ApiHandler):
    def get(self):
        self.render_json({
            'order_id': Order.generate_id()
        })
