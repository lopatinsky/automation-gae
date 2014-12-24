__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Client, Venue, READY_ORDER, BONUS_PAYMENT_TYPE,\
    CANCELED_BY_BARISTA_ORDER, CANCELED_BY_CLIENT_ORDER
from datetime import datetime
from methods import PROJECT_STARTING_YEAR, suitable_date
from google.appengine.ext import ndb


class ReportedClient:
    def __init__(self, client_id, name, tel, order_sum, payment, is_cancel):
        self.client_id = client_id
        self.name = name
        self.tel = tel
        self.amount_orders = 1
        self.average_order_cost = order_sum
        if not is_cancel:
            self.success_sum = order_sum
            self.payment = payment
            self.cancel_number = 0
            self.cancel_sum = 0
        else:
            self.success_sum = 0
            self.payment = 0
            self.cancel_number = 1
            self.cancel_sum = order_sum

    def add_order(self, order_sum, payment, is_cancel):
        self.amount_orders += 1
        if not is_cancel:
            self.success_sum += order_sum
            self.payment += payment
        else:
            self.cancel_number += 1
            self.cancel_sum += order_sum
        self.average_order_cost = (self.success_sum + self.cancel_sum) / self.amount_orders


class ClientsReportHandler(BaseHandler):
    @staticmethod
    def clients_table(chosen_year=0, chosen_month=0, chosen_day=0, venue_id=0):
        clients = {}
        query = Order.query(Order.date_created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
        if venue_id != 0:
            query = query.filter(Order.venue_id == venue_id)
        query = query.filter(ndb.OR(Order.status == READY_ORDER,
                                    Order.status == CANCELED_BY_BARISTA_ORDER,
                                    Order.status == CANCELED_BY_CLIENT_ORDER))
        for order in query.fetch():
            client_id = order.client_id
            total_sum = sum(item.get().price for item in order.items)
            payment = order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0
            if client_id in clients:
                clients[client_id].add_order(total_sum, payment,
                                             order.status != READY_ORDER)
            else:
                client = Client.get_by_id(client_id)
                clients[client_id] = ReportedClient(client_id, client.name, client.tel, total_sum, payment,
                                                    order.status != READY_ORDER)
        return clients, \
            sum(client.amount_orders for client in clients.values()), \
            sum(client.success_sum for client in clients.values()), \
            sum(client.payment for client in clients.values()), \
            sum(client.cancel_number for client in clients.values()), \
            sum(client.cancel_sum for client in clients.values())

    def get(self):
        # selected_*param == 0 if choose all *param
        venue_id = self.request.get("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year:
            chosen_month = 0
        if not chosen_month:
            chosen_day = 0
        if not venue_id:
            venue_id = 0
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            venue_id = int(venue_id)
        clients, venue_total_number, venue_total_cost, venue_total_payment, venue_c_number, venue_c_sum = \
            self.clients_table(chosen_year, chosen_month, chosen_day, venue_id)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        values = {
            'venues': Venue.query().fetch(),
            'clients': clients.values(),
            'venue_number': venue_total_number,
            'venue_expenditure': venue_total_cost,
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
        self.render('reported_clients.html', **values)