__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import Order, Client, Venue, MenuItem, READY_ORDER, BONUS_PAYMENT_TYPE
from datetime import datetime

PROJECT_STARTING_YEAR = 2013

class ReportHandler(BaseHandler):
    def get(self):
        self.render('report.html')

def correspond_date(date, day, month, year):
    if date.day != day and day != 0: return False
    if date.month != month and month != 0: return False
    if date.year != year and year != 0: return False
    return True

class ReportedClient:
    def __init__(self, id, name, tel, order_sum, payment):
        self.id = id
        self.name = name
        self.tel = tel
        self.amount_orders = 1
        self.total_sum = order_sum
        self.payment = payment
        self.average_order_cost = order_sum
    def addOrder(self, order_sum, payment):
        self.amount_orders += 1
        self.total_sum += order_sum
        self.payment += payment
        self.average_order_cost = self.total_sum / self.amount_orders

class ClientsReportHandler(BaseHandler):

    @staticmethod
    def clients_table(chosen_year=0, chosen_month=0, chosen_day=0, venue_id=0):
        clients = {}
        total_number = 0
        total_cost = 0
        total_payment = 0
        query = Order.query(Order.status == READY_ORDER)
        if venue_id != 0:
            query = query.filter(Order.venue_id == venue_id)
        for order in query.fetch():
            if not correspond_date(order.delivery_time, chosen_day, chosen_month, chosen_year):
                continue
            client_id = order.client_id
            if client_id in clients:
                clients[client_id].addOrder(order.total_sum, payment)
            else:
                client = Client.get_by_id(client_id)
                total_sum = sum(item.get().price for item in order.items)
                payment = order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0
                clients[client_id] = ReportedClient(client_id, client.name, client.tel, total_sum, payment)

        return clients,\
               sum(client.amount_orders for client in clients.values()),\
               sum(client.total_sum for client in clients.values()),\
               sum(client.payment for client in clients.values())

    def get(self):
        # selected_*param == 0 if choose all *pararm
        venue_id = self.request.get_range("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")

        clients, venue_total_number, venue_total_cost, venue_total_payment = self.clients_table(chosen_year, chosen_month, chosen_day, venue_id)
        chosen_venue = Venue.get_by_id(venue_id) if venue_id else None
        values = {
            'venues': Venue.query().fetch(),
            'clients': clients.values(),
            'venue_number': venue_total_number,
            'venue_expenditure': venue_total_cost,
            'venue_payment': venue_total_payment,
            'chosen_venue': chosen_venue,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day
        }
        self.render('reported_clients.html', **values)

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
        query = Order.query(Order.status == READY_ORDER)
        if venue_id != 0:
            query = query.filter(Order.venue_id == venue_id)
        for order in query.fetch():
            if not correspond_date(order.delivery_time, chosen_day, chosen_month, chosen_year):
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
        values = {
            'venues': Venue.query().fetch(),
            'menu_items': menu_items.values(),
            'menu_item_number': menu_item_total_number,
            'menu_item_expenditure': menu_item_total_sum,
            'chosen_venue': chosen_venue,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day
        }
        self.render('reported_menu_items.html', **values)