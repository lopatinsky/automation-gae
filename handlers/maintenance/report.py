__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import Order, Client, Venue, MenuItem, READY_ORDER
from datetime import datetime

PROJECT_STARTING_YEAR = 2013

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
        self.amountOrders += 1
        self.totalSum += orderSum
        self.averageOrderCost = self.totalSum / self.amountOrders

class ClientsReportHandler(BaseHandler):

    @staticmethod
    def clients_table(chosen_year=0, chosen_month=0, chosen_day=0, venue_id=0):
        clients = {}
        total_number = 0
        total_cost = 0
        orders = Order.query(Order.venue_id == venue_id, Order.status == READY_ORDER).fetch() if venue_id != 0 else Order.query().fetch()
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

            total_number += 1
            total_cost += order.total_sum
        return clients, total_number, total_cost

    def get(self):
        # selected_*param == 0 if choose all *pararm
        venue_id = self.request.get_range("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")

        clients, venue_total_number, venue_total_cost = self.clients_table(chosen_year, chosen_month, chosen_day, venue_id)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        self.render('reported_clients.html', venues=Venue.query().fetch(), clients=clients.values(),
                    venue_number=venue_total_number, venue_expenditure=venue_total_cost, chosen_venue=chosen_venue,
                    start_year=PROJECT_STARTING_YEAR, end_year=datetime.now().year, chosen_year=chosen_year,
                    chosen_month=chosen_month, chosen_day=chosen_day)

class ReportedMenuItem:
     def __init__(self, id, title, price):
         self.id = id
         self.title = title
         self.price = price
         self.order_number = 1
     def add_order(self):
         self.order_number += 1

class MenuItemsReportHandler(BaseHandler):
    @staticmethod
    def menu_items_table(chosen_year=0, chosen_month=0, chosen_day=0, venue_id=0):
        suited_menu_items = {}
        for order in Order.query(Order.venue_id == venue_id, Order.status == READY_ORDER).fetch() if venue_id != 0 else Order.query().fetch():
            if order.delivery_time.year != chosen_year and chosen_year != 0: # TODO erase this bidlo-code
                continue
            if order.delivery_time.month != chosen_month and chosen_month != 0: # TODO erase and this bidlo-code
                continue
            if order.delivery_time.day != chosen_day and chosen_day != 0: # TODO erase and this bidlo-code
                continue
            for item_in_order in order.items:
                item_id = item_in_order.id()
                if item_id in suited_menu_items:
                    suited_menu_items[item_id].add_order()
                else:
                    item = MenuItem.get_by_id(item_id)
                    suited_menu_items[item_id] = ReportedMenuItem(item_id, item.title, item.price)

        total_number = 0
        total_sum = 0
        for item in suited_menu_items.values():
            total_number += item.order_number
            total_sum += item.order_number * item.price

        return suited_menu_items, total_number, total_sum

    def get(self):
        # selected_*param == 0 if choose all *pararm
        venue_id = self.request.get_range("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        menu_items, menu_item_total_number, menu_item_total_sum = self.menu_items_table(chosen_year, chosen_month, chosen_day, venue_id)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        self.render('reported_menu_items.html', venues=Venue.query().fetch(), menu_items=menu_items.values(),
                    menu_item_number=menu_item_total_number, menu_item_expenditure=menu_item_total_sum,  chosen_venue=chosen_venue,
                    start_year=PROJECT_STARTING_YEAR, end_year=datetime.now().year, chosen_year=chosen_year,
                    chosen_month=chosen_month, chosen_day=chosen_day)