__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import Order, Client, Venue
from datetime import datetime

PROJECT_STARTING_YEAR = 2013
MONTHS_NUMBER = range(1, 12 + 1)

class ReportHandler(BaseHandler):
    def get(self):
        self.render('report.html')

class ReportedClient:
    def __init__(self, id, name, tel, orderSum):
        self.id = id
        self.name = name
        self.tel = tel
        self.amountOrders = 1
        self.totalSum = orderSum
        self.averageOrderCost = orderSum
    def addOrder(self, orderSum):
        self.amountOrders = self.amountOrders + 1
        self.totalSum = self.totalSum + orderSum
        self.averageOrderCost = self.totalSum / self.amountOrders

class ClientReportHandler(BaseHandler):

    def clientsTable(self, venue_id, chosen_year, chosen_month, chosen_day):
        orders = Order.query(Order.venue_id == venue_id).fetch() if venue_id != 0 else Order.query().fetch()
        clients = {}
        total_number = 0
        total_cost = 0
        for order in orders:
            if order.delivery_time.year != chosen_year and chosen_year != 0: # TODO erase this bidlo-code
                continue
            if order.delivery_time.month != chosen_month and chosen_month != 0: # TODO erase and this bidlo-code
                continue
            if order.delivery_time.day != chosen_day and chosen_day != 0: # TODO erase and this bidlo-code
                continue
            client_id = order.client_id
            if client_id in clients:
                clients[client_id].addOrder(order.total_sum)
            else:
                client = Client.get_by_id(client_id)
                clients[client_id] = ReportedClient(client_id, client.name, client.tel, order.total_sum)
            total_number = total_number + 1
            total_cost = total_cost + order.total_sum
        return clients, total_number, total_cost

    def get(self):
        # get selected_venue == 0 if choose all venues
        # get selected_year == 0 if choose all years
        # get selected_month == 0 if choose all months
        # get selected_day == 0 if choose all days
        venue_id = self.request.get_range("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")

        clients, venue_total_number, venue_total_cost = self.clientsTable(venue_id, chosen_year, chosen_month, chosen_day)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        self.render('clients.html', venues=Venue.query().fetch(), clients=clients.values(),
                    venue_number=venue_total_number, venue_expenditure=venue_total_cost, chosen_venue=chosen_venue,
                    start_year=PROJECT_STARTING_YEAR, end_year=datetime.now().year, chosen_year=chosen_year,
                    chosen_month=chosen_month, chosen_day=chosen_day)