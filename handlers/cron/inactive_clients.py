# coding: utf-8
from itertools import izip

from methods.empatika_promos import get_user_points
from methods.empatika_wallet import get_balance
from models.push import SimplePush

__author__ = 'aaryabukha'

from webapp2 import RequestHandler
from models import Client, Order, GiftMenuItem, STATUS_AVAILABLE
from models.config.config import config
from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from methods.orders.promos import get_registration_days
from methods.sms.sms_pilot import send_sms
from models.config.inactive_clients import NO_ORDERS, NEW_USER, WITH_CASHBACK, N_POINTS_LEFT
from models.specials import ClientSmsSending, ClientPushSending
from models.order import NOT_CANCELED_STATUSES


def get_orders_num(client):
    return Order.query(Order.client_id == client.key.id()).count()


def get_first_order(client):
    return Order.query(Order.client_id == client.key.id(), Order.status.IN(NOT_CANCELED_STATUSES)).get()


def days_from_last_order(client):
    last_order = Order.query(Order.client_id == client.key.id()).order(-Order.date_created).get()
    if last_order:
        today = datetime.today()
        return (today - last_order.date_created).days
    else:
        return None


def get_clients_and_texts_by_module_logic(module, clients):
    new_clients = []
    texts = []

    cheapest_gift = get_cheapest_gift()

    for client in clients:
        if module.type == WITH_CASHBACK:
            # if client has no orders – no purpose to check his points wallet balance
            if not get_orders_num(client):
                continue

            order_days = days_from_last_order(client)

            text = module.conditions.get(order_days)

            if not text:
                continue

            client_wallet_balance = get_wallet_balance(client)
            needed_cashback = module.needed_cashback

            if client_wallet_balance < needed_cashback:
                # if client's cashback is not enough – skipping him
                continue

            texts.append(module.conditions[order_days])

        elif module.type == N_POINTS_LEFT:
            # if client has no orders – no purpose to check his points balance
            if not get_orders_num(client):
                continue

            order_days = days_from_last_order(client)

            text = module.conditions.get(order_days)

            if not text:
                continue

            client_points_balance = get_points_balance(client)

            points_delta = cheapest_gift.points - client_points_balance

            if points_delta != module.needed_points_left:
                continue

            texts.append(text)

        if module.type == NO_ORDERS:
            # last order was N days ago
            order_days = days_from_last_order(client)

            text = module.conditions.get(order_days)
            if not text:
                # there is no condition for client's last order date
                continue

            texts.append(text)

        elif module.type == NEW_USER:
            # user is not already new
            if get_orders_num(client) >= 1:
                continue

            # checking how many days ago did he register
            days_registered = get_registration_days(client)

            text = module.conditions.get(days_registered)
            if not text:
                # there is no condition for client's registration date
                continue
            texts.append(text)

        new_clients.append(client)

    return new_clients, texts


def get_cheapest_gift():
    return GiftMenuItem.query(GiftMenuItem.status == STATUS_AVAILABLE).order(GiftMenuItem.points).get()


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
        return None


def get_points_balance(client):
    if config.PROMOS_API_KEY:
        return get_user_points(client.key.id())
    else:
        return None


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


def should_push(module):
    return module.should_push


class InactiveUsersNotificationHandler(RequestHandler):
    def apply_module(self, module):
        if not module or not module.status:
            return

        all_clients = get_clients()
        clients, texts = get_clients_and_texts_by_module_logic(module, all_clients)

        for client, text in izip(clients, texts):

            if should_sms(module, client):
                deferred.defer(send_sms, [client.tel], text)
                ClientSmsSending(client=client.key, sms_type=module.type).put()

            if should_push(module):
                push = SimplePush(text=module.text, header=module.header, full_text=text, client=client,
                                  namespace=namespace_manager.get_namespace(), should_popup=True, push_id=module.type)

                deferred.defer(push.send)
                ClientPushSending(client=client.key, type=module.type).put()

    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            if not config:
                continue
            for module in config.INACTIVE_NOTIFICATION_MODULE:
                self.apply_module(module)
