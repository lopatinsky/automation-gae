from .base import AdminApiHandler


class OrderListBaseHandler(AdminApiHandler):
    def _get_orders(self):
        return []

    def get(self):
        orders = self._get_orders()
        self.render_json({'orders': [order.dict() for order in orders]})


class CurrentOrdersHandler(OrderListBaseHandler):
    def _get_orders(self):
        return []  # TODO get current orders


class ReturnsHandler(OrderListBaseHandler):
    def _get_orders(self):
        return []  # TODO get returns


class HistoryHandler(OrderListBaseHandler):
    def _get_orders(self):
        return []  # TODO search history
