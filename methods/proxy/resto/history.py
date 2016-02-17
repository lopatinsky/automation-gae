from datetime import datetime, timedelta
from google.appengine.ext import ndb

from methods.proxy.resto.payment_types import PAYMENT_TYPE_MAP
from methods.proxy.resto.requests import get_resto_order_info
from methods.proxy.resto.venues import get_venues
from methods.rendering import STR_DATETIME_FORMAT
from models import Order, Address, MenuItem, GroupModifier, SingleModifier
from models.order import OrderPositionDetails, READY_ORDER, ChosenGroupModifierDetails, NEW_ORDER, \
    CANCELED_BY_BARISTA_ORDER, CONFIRM_ORDER
from models.payment_types import CASH_PAYMENT_TYPE
from models.proxy.resto import RestoCompany, RestoClient
from models.venue import SELF, DELIVERY
from requests import get_resto_history

__author__ = 'dvpermyakov'


def _get_status_from_resto_status(resto_company, resto_status):
    STATUS_MAP = {
        1: NEW_ORDER,
        3: READY_ORDER,
        4: CANCELED_BY_BARISTA_ORDER
    }

    if resto_status == 2:
        if resto_company.enable_delivery_confirmation:
            return CONFIRM_ORDER
        else:
            return NEW_ORDER
    else:
        return STATUS_MAP[resto_status]


def _get_address(resto_address):
    address = Address()
    address.city = resto_address.get('city')
    address.street = resto_address.get('street')
    address.home = resto_address.get('home')
    return address


def _get_modifiers(resto_modifiers):
    group_modifiers = []
    single_modifiers = []
    for resto_modifier in resto_modifiers:
        if resto_modifier.get('groupId'):
            modifier = ChosenGroupModifierDetails()
            modifier.group_modifier = ndb.Key(GroupModifier, resto_modifier['groupId'])
            modifier.group_choice_id_str = resto_modifier['id']
            group_modifiers.append(modifier)
        else:
            single_modifiers.append(ndb.Key(SingleModifier, resto_modifier['id']))
    return group_modifiers, single_modifiers


def _get_item_details(resto_item):
    detail = OrderPositionDetails()
    detail.item = ndb.Key(MenuItem, resto_item['id'])
    detail.price = int(resto_item['sum'] * 100)
    detail.revenue = int(resto_item['sum'] * 100)
    detail.group_modifiers, detail.single_modifiers = _get_modifiers(resto_item['modifiers'])
    return detail


def get_orders(client):
    resto_company = RestoCompany.get()
    resto_client = RestoClient.get(client)
    resto_history = get_resto_history(resto_company, resto_client).get('history', [])
    orders = []
    any_venue = get_venues()[0]  # for timezone offset
    for resto_venue_history in resto_history:
        for resto_order in resto_venue_history.get('local_history', []):
            order_id = resto_order['resto_id'] or resto_order['order_id']
            order = Order(id=order_id)
            order.client_id = client.key.id()
            if resto_order['status'] is not None:
                order.status = _get_status_from_resto_status(resto_company, resto_order['status'])
            else:
                resto_order['status'] = READY_ORDER
            order.number = int(resto_order['number'])
            order.address = _get_address(resto_order['address'])
            order.venue_id = resto_order['venue_id']
            order.total_sum = resto_order['sum']
            local_delivery_time = datetime.fromtimestamp(resto_order['date'])
            order.delivery_time = local_delivery_time - timedelta(hours=any_venue.timezone_offset)
            order.delivery_time_str = local_delivery_time.strftime(STR_DATETIME_FORMAT)
            if resto_order['payment_type'] is not None:
                order.payment_type_id = int(PAYMENT_TYPE_MAP[int(resto_order['payment_type'])])
            else:
                order.payment_type_id = CASH_PAYMENT_TYPE
            order.delivery_type = SELF if resto_order['self'] else DELIVERY
            order.item_details = [_get_item_details(resto_item) for resto_item in resto_order['items']]
            orders.append(order)
    return orders


def _convert_resto_status(resto_status):
    if resto_status in (1, 2):
        return NEW_ORDER
    elif resto_status == 3:
        return READY_ORDER
    elif resto_status == 4:
        return CANCELED_BY_BARISTA_ORDER
    return None


def update_status(order):
    resto_company = RestoCompany.get()
    resto_info = get_resto_order_info(resto_company, order.key.id())
    new_status = _convert_resto_status(resto_info['status'])
    if new_status is not None and order.status != new_status:
        order.status = new_status
        order.put()


def find_lost_order(uuid):
    resto_company = RestoCompany.get()
    resto_info = get_resto_order_info(resto_company, uuid)
    if not resto_info:
        return None
    return {
        'status': _convert_resto_status(resto_info['status']),
        'resto_id': resto_info['restoId'],
        'number': int(resto_info['number'])
    }
