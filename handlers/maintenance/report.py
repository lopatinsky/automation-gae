__author__ = 'dvpermyakov'

from .base import BaseHandler
from models import Order, Client, Venue, MenuItem, READY_ORDER, BONUS_PAYMENT_TYPE
from datetime import datetime, date, time
import calendar

PROJECT_STARTING_YEAR = 2014

class ReportHandler(BaseHandler):
    def get(self):
        self.render('report.html')

def suitable_date(day, month, year, beginning):
    if not year: month = 0
    if not month: day = 0
    if not beginning:
        if not year: year = datetime.now().year
        if not month: month = 12
        if not day: day = calendar.monthrange(year,month)[1]
        day = min(day, calendar.monthrange(year,month)[1])
        return datetime.combine(date(year, month, day), time.max)
    else:
        if not year: year = PROJECT_STARTING_YEAR
        if not month: month = 1
        if not day: day = 1
        day = min(day, calendar.monthrange(year,month)[1])
        return datetime.combine(date(year, month, day), time.min)

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
        query = Order.query(Order.status == READY_ORDER)
        query = query.filter(Order.date_created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
        if venue_id != 0:
            query = query.filter(Order.venue_id == venue_id,)
        for order in query.fetch():
            client_id = order.client_id
            total_sum = sum(item.get().price for item in order.items)
            payment = order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0
            if client_id in clients:
                clients[client_id].addOrder(total_sum, payment)
            else:
                client = Client.get_by_id(client_id)
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
        if not chosen_year: chosen_month = 0
        if not chosen_month: chosen_day = 0
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
        query = query.filter(Order.date_created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Order.date_created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
        if venue_id != 0:
            query = query.filter(Order.venue_id == venue_id)
        for order in query.fetch():
            for item_in_order in order.items:
                item_id = item_in_order.id()
                if item_id in suited_menu_items:
                    suited_menu_items[item_id].add_order()
                else:
                    item = MenuItem.get_by_id(item_id)
                    suited_menu_items[item_id] = ReportedMenuItem(item_id, item.title, item.price)
        return suited_menu_items, \
               sum(item.order_number for item in suited_menu_items.values()),\
               sum(item.order_number * item.price for item in suited_menu_items.values())

    def get(self):
        # selected_*param == 0 if choose all *pararm
        venue_id = self.request.get_range("selected_venue")
        chosen_year = self.request.get_range("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year: chosen_month = 0
        if not chosen_month: chosen_day = 0
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