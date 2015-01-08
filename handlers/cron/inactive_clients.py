__author__ = 'dvpermyakov'

from webapp2 import RequestHandler
from models import Client, Order, READY_ORDER
from methods import email
from datetime import datetime, timedelta
import logging

CLIENT_DAY_INTERVAL = 1


class SearchInactiveClientsHandler(RequestHandler):
    def get(self):
        clients_with_phone = Client.query(Client.created > datetime.now() - timedelta(days=CLIENT_DAY_INTERVAL)).fetch()
        for client in clients_with_phone[:]:
            if not client.tel:
                clients_with_phone.remove(client)
        for client in clients_with_phone[:]:
            last_order = Order.query(Order.client_id == client.key.id()).get()
            if last_order:
                clients_with_phone.remove(client)
        if not len(clients_with_phone):
            return
        else:
            body = 'Clients who bind telephone and not order anything:\n'
            for client in clients_with_phone:
                body += 'Name: %s %s, email: %s, telephone: %s\n' % (client.name, client.surname,
                                                                     client.email, client.tel)
            logging.info(body)
            email.send_error('analytics', 'Clients with telephones', body)