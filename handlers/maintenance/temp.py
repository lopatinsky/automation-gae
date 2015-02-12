__author__ = 'dvpermyakov'

from base import BaseHandler
from models import Client, Order
from datetime import datetime, timedelta


class TempHandler(BaseHandler):
    def get(self):
        clients = Client.query(Client.created > datetime.now() - timedelta(days=14))
        client_ids = [client.key.id() for client in clients]
        orders = Order.query(Order.date_created > datetime.now() - timedelta(days=14))
        for order in orders:
            client_id = order.client_id
            if client_id in client_ids:
                client_ids.remove(client_id)
        clients = [client for client in clients if client.key.id() in client_ids and client.tel]
        for client in clients:
            client.tel += ' (%s)' % client.email
            client.name += ' %s\n(%s)' % (client.surname, client.created.strftime('%Y-%m-%d %H:%M:%S'))
        self.render('reported_clients.html', clients=clients, start_year=2014, end_year=2015)