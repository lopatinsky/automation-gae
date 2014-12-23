__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Client, Venue, READY_ORDER, BONUS_PAYMENT_TYPE
from datetime import datetime
from methods import PROJECT_STARTING_YEAR, suitable_date


class ReportedClient:
    def __init__(self, client_id, name, tel, order_sum, payment):
        self.client_id = client_id
        self.name = name
        self.tel = tel
        self.amount_orders = 1
        self.total_sum = order_sum
        self.payment = payment
        self.average_order_cost = order_sum

    def add_order(self, order_sum, payment):
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
            query = query.filter(Order.venue_id == venue_id)
        for order in query.fetch():
            client_id = order.client_id
            total_sum = sum(item.get().price for item in order.items)
            payment = order.total_sum if order.payment_type_id != BONUS_PAYMENT_TYPE else 0
            if client_id in clients:
                clients[client_id].add_order(total_sum, payment)
            else:
                client = Client.get_by_id(client_id)
                clients[client_id] = ReportedClient(client_id, client.name, client.tel, total_sum, payment)
        return clients, \
            sum(client.amount_orders for client in clients.values()), \
            sum(client.total_sum for client in clients.values()), \
            sum(client.payment for client in clients.values())

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
        clients, venue_total_number, venue_total_cost, venue_total_payment = self.clients_table(chosen_year,
                                                                                                chosen_month,
                                                                                                chosen_day,
                                                                                                venue_id)
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