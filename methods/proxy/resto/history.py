from datetime import datetime
from google.appengine.ext import ndb
from models import Order, Address, MenuItem, GroupModifier
from models.order import OrderPositionDetails, READY_ORDER, ChosenGroupModifierDetails
from models.proxy.resto import RestoCompany, RestoClient
from requests import get_resto_history

__author__ = 'dvpermyakov'


def _get_address(resto_address):
    address = Address()
    address.city = resto_address.get('city')
    address.street = resto_address.get('street')
    address.home = resto_address.get('home')
    return address


def _get_group_modifier(resto_modifier):
    modifier = ChosenGroupModifierDetails()
    modifier.group_modifier = ndb.Key(GroupModifier, resto_modifier['groupId'])
    modifier.group_choice_id_str = resto_modifier['id']
    return modifier


def _get_item_details(resto_item):
    detail = OrderPositionDetails()
    detail.item = ndb.Key(MenuItem, resto_item['id'])
    detail.price = int(resto_item['sum'] * 100)
    detail.revenue = int(resto_item['sum'] * 100)
    detail.group_modifiers = [_get_group_modifier(resto_modifier) for resto_modifier in resto_item['modifiers']]
    return detail


def get_orders(client):
    resto_company = RestoCompany.get()
    resto_client = RestoClient.get(client)
    resto_history = get_resto_history(resto_company, resto_client).get('history', [])
    orders = []
    for resto_venue_history in resto_history:
        for resto_order in resto_venue_history.get('local_history', []):
            order = Order(id=resto_order['order_id'])
            order.client_id = client.key.id()
            order.status = READY_ORDER
            order.number = int(resto_order['number'])
            order.address = _get_address(resto_order['address'])
            order.venue_id = resto_order['venue_id']
            order.total_sum = resto_order['sum']
            order.delivery_time = datetime.fromtimestamp(resto_order['date'])
            order.item_details = [_get_item_details(resto_item) for resto_item in resto_order['items']]
            orders.append(order)
    return orders
