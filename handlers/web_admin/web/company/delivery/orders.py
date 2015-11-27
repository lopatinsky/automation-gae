# coding=utf-8
import copy
from datetime import datetime, timedelta
from google.appengine.api import namespace_manager
from ..base import CompanyBaseHandler
from methods.auth import delivery_rights_required
from models import Order, Client, Venue, DeliverySlot, MenuItem, SingleModifier, GroupModifier
from methods.rendering import timestamp
from methods.orders.done import done_order
from methods.orders.cancel import cancel_order
from methods.orders.confirm import confirm_order
from models.order import STATUS_MAP, NOT_CANCELED_STATUSES, NEW_ORDER, CONFIRM_ORDER, READY_ORDER, CANCELED_BY_BARISTA_ORDER
from models.payment_types import PAYMENT_TYPE_MAP
from models.venue import DELIVERY

__author__ = 'dvpermyakov'


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
        'date_str': order.date_str,
        'delivery_time_str': order.delivery_time_str,
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
        hours_offset = Venue.get_by_id(int(order.venue_id)).timezone_offset
        if order.delivery_time:
            delivery_time_str = (order.delivery_time + timedelta(hours=hours_offset)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            delivery_time_str = u''
        if order.delivery_slot_id:
            slot = DeliverySlot.get_by_id(order.delivery_slot_id)
            if slot.slot_type == DeliverySlot.STRINGS:
                if order.delivery_time:
                    delivery_time_date = order.delivery_time.strftime("%Y-%m-%d")
                else:
                    delivery_time_date = u''
                delivery_time_str = u'%s(%s)' % (delivery_time_date, slot.name)
        order.client = Client.get(order.client_id)
        extra_dict = {}
        if order.client:
            for client_dict in order.client.dict(with_extra_fields=True)['extra_data']:
                extra_dict[client_dict['title']] = client_dict['value'] if client_dict['value'] != None else u'Не введено'
            order.client.extra_data = extra_dict
        if order.address:
            order.address_str = order.address.str()
        else:
            order.address_str = u'Адрес не найден'
        order.date_str = (order.date_created + timedelta(hours=hours_offset)).strftime("%Y-%m-%d %H:%M:%S")
        order.delivery_time_str = delivery_time_str
        order.status_description = STATUS_MAP[order.status]
    return orders


def order_items_values(order):
    def _process_item_dict(item_dict, gift=False):
        item_obj = copy.copy(MenuItem.get_by_id(int(item_dict['id'])))
        item_obj.amount = item_dict['quantity']
        item_obj.total_float_price = item_obj.float_price * item_obj.amount
        item_obj.modifiers = []
        item_obj.is_gift = gift
        for modifier_dict in item_dict['single_modifiers']:
            modifier = SingleModifier.get_by_id(int(modifier_dict['id']))
            modifier.amount = modifier_dict['quantity']
            modifier.total_float_price = modifier.float_price * modifier.amount
            item_obj.total_float_price += modifier.total_float_price * item_obj.amount
            item_obj.modifiers.append(modifier)
        for modifier_dict in item_dict['group_modifiers']:
            modifier = GroupModifier.get_by_id(int(modifier_dict['id']))
            choice = modifier.get_choice_by_id(int(modifier_dict['choice']))
            choice.amount = modifier_dict['quantity']
            choice.total_float_price = choice.float_price * choice.amount
            item_obj.total_float_price += choice.total_float_price * item_obj.amount
            item_obj.modifiers.append(choice)
        if gift:
            item_obj.total_float_price = 0.0
        return item_obj

    items = []
    promos = set()
    menu_sum = 0
    for item_dict in order.grouped_item_dict(order.item_details):
        items.append(_process_item_dict(item_dict))
        menu_sum += item_dict['price'] * item_dict['quantity']
        promos.update(set(item_dict['promos']))
    promos.update(set([key.get().title for key in order.promos]))

    for gift_dict in order.grouped_item_dict(order.gift_details, True) + \
                     order.grouped_item_dict(order.order_gift_details):
        items.append(_process_item_dict(gift_dict, True))

    order = _update_order_info([order])[0]
    order.menu_sum = menu_sum
    order.promo_text = u', '.join(promos)
    order.payment_type_str = PAYMENT_TYPE_MAP[order.payment_type_id]
    return {
        'order': order,
        'items': items
    }


class DeliveryOrdersHandler(CompanyBaseHandler):
    @delivery_rights_required
    def get(self):
        orders = Order.query(Order.delivery_type == DELIVERY, Order.status.IN(NOT_CANCELED_STATUSES))\
            .order(-Order.date_created).fetch()
        orders = _update_order_info(orders)
        proxy_statuses = []
        for status in NOT_CANCELED_STATUSES:
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
    @delivery_rights_required
    def get(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        self.render('/delivery/items.html', **order_items_values(order))


class NewDeliveryOrdersHandler(CompanyBaseHandler):
    @delivery_rights_required
    def get(self):
        last_time = int(self.request.get('last_time'))
        start = datetime.fromtimestamp(last_time)
        orders = Order.query(Order.delivery_type == DELIVERY, Order.status.IN(NOT_CANCELED_STATUSES),
                             Order.date_created > start)\
            .order(-Order.date_created).fetch()
        orders = _update_order_info(orders)
        if orders:
            last_time = timestamp(orders[0].date_created) + 1
        self.render_json({
            'orders': [_order_delivery_dict(order, Client.get(order.client_id)) for order in orders],
            'last_time': last_time
        })


class ConfirmOrderHandler(CompanyBaseHandler):
    @delivery_rights_required
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        confirm_order(order, namespace_manager.get_namespace())
        self.render_json(_order_json(order, old_status))


class CloseOrderHandler(CompanyBaseHandler):
    @delivery_rights_required
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        done_order(order, namespace_manager.get_namespace())
        self.render_json(_order_json(order, old_status))


class CancelOrderHandler(CompanyBaseHandler):
    @delivery_rights_required
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        old_status = order.status
        success = cancel_order(order, CANCELED_BY_BARISTA_ORDER, namespace_manager.get_namespace())
        response = _order_json(order, old_status)
        response.update({
            'success': success
        })
        self.render_json(response)
