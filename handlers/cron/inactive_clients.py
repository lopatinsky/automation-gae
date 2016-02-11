# coding: utf-8
import logging
from methods.empatika_promos import get_user_points
from methods.empatika_wallet import get_balance
from models.push import SimplePush

__author__ = 'aaryabukha'

from webapp2 import RequestHandler
from models import Client, Order
from models.config.config import config
from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from methods.orders.promos import check_registration_date
from methods.sms.sms_pilot import send_sms

from models.config.inactive_clients import NEW_USERS_WITH_NO_ORDERS, USERS_WITH_ONE_ORDER
from models.specials import ClientSmsSending, ClientPushSending
from models.order import NOT_CANCELED_STATUSES


def get_orders_num(client):
    return len(Order.query(Order.client_id == client.key.id()).fetch())


def get_first_order(client):
    return Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()


def days_from_last_order(client):
    last_order = Order.query(Order.client_id == client.key.id()).order(-Order.date_created).get()
    if last_order:
        today = datetime.today()
        return (today - last_order.date_created).days
    else:
        return None


def filter_clients_by_module_logic(module, clients):
    new_clients = []
    for client in clients:
        if module.type == NEW_USERS_WITH_NO_ORDERS:
            if not check_registration_date(client, module.days) or get_orders_num(client) >= 1:
                continue
        elif module.type == USERS_WITH_ONE_ORDER:
            if get_orders_num(client) != 1 and days_from_last_order(client) >= module.days:
                continue
        new_clients.append(client)
    return new_clients


def get_clients():
    namespace = namespace_manager.get_namespace()
    namespace_manager.set_namespace('')  # query global clients
    result = Client.query(Client.namespace_created == namespace).fetch()
    namespace_manager.set_namespace(namespace)
    result.extend(Client.query().fetch())
    return result


def get_wallet_balance(client):
    if config.WALLET_ENABLED:
        return get_balance(client.key.id())
    else:
        return 0


def get_points_balance(client):
    if config.PROMOS_API_KEY:
        return get_user_points(client.key.id())
    else:
        return 0


def should_sms(module, client):
    wallet_balance = get_wallet_balance(client)
    points_balance = get_points_balance(client)

    if module.should_sms:
        return True
    elif module.sms_if_has_points and module.sms_if_has_cashback:
        return wallet_balance or points_balance
    elif module.sms_if_has_points:
        return points_balance
    elif module.sms_if_has_cashback:
        return wallet_balance
    return False


def should_push(module, client):
    return module.should_push


class NotificatingInactiveUsersHandler(RequestHandler):
    def apply_module(self, module):
        if not module or not module.status:
            return

        all_clients = get_clients()
        clients = filter_clients_by_module_logic(module, all_clients)
        logging.debug('{0}, {1}'.format(module, clients))
        for client in clients:
            text = module.text

            if should_sms(module, client):
                deferred.defer(send_sms, [client.tel], text)
                ClientSmsSending(client=client.key, sms_type=module.type).put()

            if should_push(module, client):
                push = SimplePush(text=module.text, header=module.header, full_text=text, client=client,
                                  namespace=namespace_manager.get_namespace(), should_popup=True)

                deferred.defer(push.send)
                ClientPushSending(client=client.key, type=module.type).put()

    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            if not config:
                continue
            for module in config.NOTIFICATING_INACTIVE_USERS_MODULE:
                self.apply_module(module)
