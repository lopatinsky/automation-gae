from datetime import datetime, timedelta
from google.appengine.ext import ndb
from methods.proxy.resto.requests import get_resto_order_info
from methods.proxy.resto.venues import get_venues
from methods.rendering import STR_DATETIME_FORMAT
from models import Order, Address, MenuItem, GroupModifier, SingleModifier
from models.order import OrderPositionDetails, READY_ORDER, ChosenGroupModifierDetails, NEW_ORDER, \
    CANCELED_BY_BARISTA_ORDER
from models.payment_types import CASH_PAYMENT_TYPE
from models.proxy.resto import RestoCompany, RestoClient
from models.venue import SELF, DELIVERY
from requests import get_resto_history

__author__ = 'dvpermyakov'


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
            order = Order(id=resto_order['order_id'])
            order.client_id = client.key.id()
            order.status = READY_ORDER
            order.number = int(resto_order['number'])
            order.address = _get_address(resto_order['address'])
            order.venue_id = resto_order['venue_id']
            order.total_sum = resto_order['sum']
            local_delivery_time = datetime.fromtimestamp(resto_order['date'])
            order.delivery_time = local_delivery_time - timedelta(hours=any_venue.timezone_offset)
            order.delivery_time_str = local_delivery_time.strftime(STR_DATETIME_FORMAT)
            order.payment_type_id = CASH_PAYMENT_TYPE  # todo: this is hardcoded
            order.delivery_type = SELF if resto_order['self'] else DELIVERY
            order.item_details = [_get_item_details(resto_item) for resto_item in resto_order['items']]
            orders.append(order)
    return orders


def update_status(order):
    resto_company = RestoCompany.get()
    resto_info = get_resto_order_info(resto_company, order.key.id())
    resto_status = resto_info['status']
    new_status = None
    if resto_status in (1, 2):
        new_status = NEW_ORDER
    elif resto_status == 3:
        new_status = READY_ORDER
    elif resto_status == 4:
        new_status = CANCELED_BY_BARISTA_ORDER
    if new_status is not None and order.status != new_status:
        order.status = new_status
        order.put()
