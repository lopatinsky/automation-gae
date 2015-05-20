# coding=utf-8
from datetime import datetime, timedelta
import logging
from ..base import CompanyBaseHandler
from models import Order, DELIVERY, NEW_ORDER, Client, STATUS_MAP, CONFIRM_ORDER, READY_ORDER, \
    CANCELED_BY_BARISTA_ORDER, Venue
from methods.rendering import timestamp

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


class DeliveryOrdersHandler(CompanyBaseHandler):
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
    def get(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        logging.info(order.dict())
        items = []
        for item_detail in order.item_details:
            item_obj = item_detail.item.get()
            item_obj.modifiers = []
            for modifier in item_detail.single_modifiers:
                item_obj.modifiers.append(modifier.get())
            item_obj.modifiers.extend(item_detail.group_modifiers)
            items.append(item_obj)
        order = _update_order_info([order])[0]
        self.render('/delivery/items.html', **{
            'order': order,
            'items': items
        })


class NewDeliveryOrdersHandler(CompanyBaseHandler):
    def get(self):
        last_time = int(self.request.get('last_time'))
        logging.info(last_time)
        start = datetime.fromtimestamp(last_time)
        orders = Order.query(Order.delivery_type == DELIVERY, Order.status.IN(STATUSES), Order.date_created > start)\
            .order(-Order.date_created).fetch()
        orders = _update_order_info(orders)
        if orders:
            last_time = timestamp(orders[0].date_created) + 1
        logging.info(last_time)
        logging.info(orders)
        self.render_json({
            'orders': [_order_delivery_dict(order, Client.get_by_id(order.client_id)) for order in orders],
            'last_time': last_time
        })


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