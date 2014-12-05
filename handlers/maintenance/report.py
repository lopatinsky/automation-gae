from .base import BaseHandler
from models import Order, Client, Venue
import logging

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

    def clientsTable(self, venue_id):
        orders = Order.query().fetch()
        map = {}  # TODO rename
        total_number = 0
        total_cost = 0
        for order in orders:
            if order.venue_id != venue_id:  # TODO query only required venue
                continue
            id = order.client_id
            if id in map:
                map[id].addOrder(order.total_sum)
            else:
                client = Client.get_by_id(id)
                map[id] = ReportedClient(id, client.name, client.tel, order.total_sum)
            total_number = total_number + 1
            total_cost = total_cost + order.total_sum
        return map, total_number, total_cost

    def get(self):
        venue_id = self.request.get_range("selectedVenue")
        clients_info = self.clientsTable(venue_id)  # TODO assign to three names
        self.render('clients.html', venues=Venue.query().fetch(), clients=clients_info[0].values(),
                    venue_number=clients_info[1], venue_expenditure=clients_info[2], current_venue=Venue.get_by_id(venue_id))
