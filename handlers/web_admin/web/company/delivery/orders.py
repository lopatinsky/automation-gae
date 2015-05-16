import logging
from ..base import CompanyBaseHandler
from models import Order, DELIVERY, NEW_ORDER, Client, STATUS_MAP, CONFIRM_ORDER, READY_ORDER, \
    CANCELED_BY_BARISTA_ORDER

__author__ = 'dvpermyakov'


def _order_json(order, old_status):
    return {
        'order_id': order.key.id(),
        'old_status': old_status,
        'status': order.status,
        'status_description': STATUS_MAP[order.status]
    }


class DeliveryOrdersHandler(CompanyBaseHandler):
    def get(self):
        statuses = [
            NEW_ORDER,
            CONFIRM_ORDER,
            READY_ORDER,
            CANCELED_BY_BARISTA_ORDER
        ]
        orders = Order.query(Order.delivery_type == DELIVERY, Order.status.IN(statuses)).order(-Order.delivery_time).fetch()
        for order in orders:
            order.client = Client.get_by_id(order.client_id)
            order.status_description = STATUS_MAP[order.status]
        proxy_statuses = []
        for status in statuses:
            proxy_statuses.append({
                'value': status,
                'name': STATUS_MAP[status]
            })
        #last_time =
        self.render('/delivery/orders.html', **{
            #'last_time':
            'orders': orders,
            'statuses': proxy_statuses,
            'status_new': NEW_ORDER,
            'status_confirmed': CONFIRM_ORDER,
            'status_closed': READY_ORDER,
            'status_cancelled': CANCELED_BY_BARISTA_ORDER
        })


class OrderItemsHandler(CompanyBaseHandler):
    def get(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        items = []
        for item_detail in order.item_details:
            item_obj = item_detail.item.get()
            item_obj.float_price = item_obj.price / 100.0
            items.append(item_obj)
        self.render('/delivery/items.html', **{
            'order': order,
            'items': items
        })


class NewDeliveryOrdersHandler(CompanyBaseHandler):
    def get(self):
        pass


class ConfirmOrderHandler(CompanyBaseHandler):
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        order.confirm_order()
        self.render_json(_order_json(order, old_status))


class CloseOrderHandler(CompanyBaseHandler):
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        order.close_order()
        self.render_json(_order_json(order, old_status))


class CancelOrderHandler(CompanyBaseHandler):
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        order.cancel_order()
        self.render_json(_order_json(order, old_status))