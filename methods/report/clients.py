from models.order import READY_ORDER, CANCELED_BY_BARISTA_ORDER, CANCELED_BY_CLIENT_ORDER

__author__ = 'dvpermyakov'

from models import Order, Client, Venue
from datetime import datetime
from report_methods import PROJECT_STARTING_YEAR, suitable_date
from google.appengine.ext import ndb


class ReportedClient:
    def __init__(self, client_id, name, tel, venue_sum, order_sum, payment, is_cancel, device_type):
        self.client_id = client_id
        self.name = name
        self.tel = tel
        self.amount_orders = 0
        self.device_type = device_type
        self.cancel_number = 0
        self.venue_sum = 0
        self.cancel_sum = 0
        self.menu_sum = 0
        self.payment = 0
        self.average_order_cost = 0

        self.add_order(venue_sum, order_sum, payment, is_cancel)

    def add_order(self, venue_sum, order_sum, payment, is_cancel):
        self.amount_orders += 1
        if not is_cancel:
            self.venue_sum += venue_sum
            self.menu_sum += order_sum
            self.payment += payment
        else:
            self.cancel_number += 1
            self.cancel_sum += venue_sum
        self.average_order_cost = (self.venue_sum+ self.cancel_sum) / self.amount_orders


def clients_table(chosen_year=0, chosen_month=0, chosen_day=0, venue_id=0, chosen_days=None):
    clients = {}
    if chosen_days:
        chosen_days = [int(day) for day in chosen_days]
        min_day = min(chosen_days)
        max_day = max(chosen_days)
        query = Order.query(Order.date_created >= suitable_date(min_day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(max_day, chosen_month, chosen_year, False))
    else:
        query = Order.query(Order.date_created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
    if venue_id != 0:
        query = query.filter(Order.venue_id == venue_id)
    query = query.filter(ndb.OR(Order.status == READY_ORDER,
                                Order.status == CANCELED_BY_BARISTA_ORDER,
                                Order.status == CANCELED_BY_CLIENT_ORDER))
    for order in query.fetch():
        client_id = order.client_id
        total_sum = sum(item.price for item in order.item_details)
        payment = order.total_sum - order.wallet_payment
        venue_sum = sum(d_item.revenue for d_item in order.item_details)
        if client_id in clients:
            clients[client_id].add_order(venue_sum, total_sum, payment,
                                         order.status != READY_ORDER)
        else:
            client = Client.get_by_id(client_id)
            clients[client_id] = ReportedClient(client_id, '%s %s' % (client.name, client.surname), client.tel, venue_sum, total_sum, payment,
                                                order.status != READY_ORDER, order.device_type)
    return clients, \
        sum(client.amount_orders for client in clients.values()), \
        sum(client.venue_sum for client in clients.values()), \
        sum(client.menu_sum for client in clients.values()), \
        sum(client.payment for client in clients.values()), \
        sum(client.cancel_number for client in clients.values()), \
        sum(client.cancel_sum for client in clients.values())


def get(venue_id, chosen_year, chosen_month, chosen_day=None, chosen_days=None):
    if not venue_id:
        venue_id = 0
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_day = datetime.now().day
    else:
        venue_id = int(venue_id)

    if not chosen_year:
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_day = datetime.now().day
    else:
        chosen_year = int(chosen_year)

    if not chosen_year:
        chosen_month = 0
    if not chosen_month:
        chosen_day = 0

    if not chosen_days:
        clients, venue_total_number, venue_revenue, venue_menu_cost, venue_total_payment, venue_c_number, venue_c_sum = \
            clients_table(chosen_year, chosen_month, chosen_day, venue_id)
    else:
        clients, venue_total_number, venue_revenue, venue_menu_cost, venue_total_payment, venue_c_number, venue_c_sum = \
            clients_table(chosen_year, chosen_month, chosen_day, venue_id, chosen_days)
    chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
    values = {
        'venues': Venue.query().fetch(),
        'clients': clients.values(),
        'venue_number': venue_total_number,
        'venue_revenue': venue_revenue,
        'venue_expenditure': venue_menu_cost,
        'venue_payment': venue_total_payment,
        'venue_cancel_number': venue_c_number,
        'venue_cancel_sum': venue_c_sum,
        'chosen_venue': chosen_venue,
        'start_year': PROJECT_STARTING_YEAR,
        'end_year': datetime.now().year,
        'chosen_year': chosen_year,
        'chosen_month': chosen_month,
        'chosen_day': chosen_day
    }
    return values