# coding=utf-8
from datetime import datetime, timedelta
from ..base import CompanyBaseHandler
from methods.auth import company_user_required
from models import Order, DELIVERY, NEW_ORDER, Client, STATUS_MAP, CONFIRM_ORDER, READY_ORDER, \
    CANCELED_BY_BARISTA_ORDER, Venue
from methods.rendering import timestamp
from methods.orders.done import done_order
from methods.orders.cancel import cancel_order
from methods.orders.confirm import confirm_order

__author__ = 'dvpermyakov'

STATUSES = [
    NEW_ORDER,
    CONFIRM_ORDER,
    READY_ORDER,
    CANCELED_BY_BARISTA_ORDER
]


def _order_json(order, old_status):
    return {
        'order_id': order.key.id(),
        'old_status': old_status,
        'status': order.status,
        'status_description': STATUS_MAP[order.status]
    }


def _order_delivery_dict(order, client):
    return {
        'order_id': order.key.id(),
        'address': order.address.str() if order.address else u'Адрес не найден',
        'date_str': datetime.strftime(order.date_created + timedelta(hours=Venue.get_by_id(order.venue_id).timezone_offset),
                                      "%Y-%m-%d %H:%M:%S"),
        'delivery_time': order.delivery_time if order.delivery_time else order.delivery_slot,
        'total_sum': order.total_sum,
        'client': {
            'name': client.name,
            'surname': client.surname,
            'phone': client.tel
        },
        'status': order.status,
        'status_description': STATUS_MAP[order.status]
    }


def _update_order_info(orders):
    for order in orders:
        order.client = Client.get_by_id(order.client_id)
        if order.address:
            order.address_str = order.address.str()
        else:
            order.address_str = u'Адрес не найден'
        order.date_str = datetime.strftime(order.date_created + timedelta(hours=Venue.get_by_id(order.venue_id).timezone_offset),
                                           "%Y-%m-%d %H:%M:%S")
        order.status_description = STATUS_MAP[order.status]
    return orders


def order_items_values(order):
    items = []
    for item_detail in order.item_details:
        item_obj = item_detail.item.get()
        item_obj.modifiers = []
        for modifier in item_detail.single_modifiers:
            item_obj.modifiers.append(modifier.get())
        item_obj.modifiers.extend(item_detail.group_modifiers)
        items.append(item_obj)
    order = _update_order_info([order])[0]
    return {
        'order': order,
        'items': items
    }


class DeliveryOrdersHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        orders = Order.query(Order.delivery_type == DELIVERY, Order.status.IN(STATUSES))\
            .order(-Order.date_created).fetch()
        orders = _update_order_info(orders)
        proxy_statuses = []
        for status in STATUSES:
            proxy_statuses.append({
                'value': status,
                'name': STATUS_MAP[status]
            })
        if orders:
            last_time = timestamp(orders[0].date_created) + 1
        else:
            last_time = 0
        self.render('/delivery/orders.html', **{
            'last_time': last_time,
            'orders': orders,
            'statuses': proxy_statuses,
            'status_new': NEW_ORDER,
            'status_confirmed': CONFIRM_ORDER,
            'status_closed': READY_ORDER,
            'status_cancelled': CANCELED_BY_BARISTA_ORDER
        })


class OrderItemsHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        self.render('/delivery/items.html', **order_items_values(order))


class NewDeliveryOrdersHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        last_time = int(self.request.get('last_time'))
        start = datetime.fromtimestamp(last_time)
        orders = Order.query(Order.delivery_type == DELIVERY, Order.status.IN(STATUSES), Order.date_created > start)\
            .order(-Order.date_created).fetch()
        orders = _update_order_info(orders)
        if orders:
            last_time = timestamp(orders[0].date_created) + 1
        self.render_json({
            'orders': [_order_delivery_dict(order, Client.get_by_id(order.client_id)) for order in orders],
            'last_time': last_time
        })


class ConfirmOrderHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        confirm_order(order)
        self.render_json(_order_json(order, old_status))


class CloseOrderHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        done_order(order)
        self.render_json(_order_json(order, old_status))


class CancelOrderHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        success = cancel_order(order, CANCELED_BY_BARISTA_ORDER)
        response = _order_json(order, old_status)
        response.update({
            'success': success
        })
        self.render_json(response)