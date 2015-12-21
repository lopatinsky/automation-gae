# coding: utf-8
from methods.empatika_promos import get_user_points
from methods.empatika_wallet import get_balance
from models.push import SimplePush

__author__ = 'aaryabukha'

from webapp2 import RequestHandler
from models import Client, Order
from models.config.config import Config
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
            if not check_registration_date(client, module.days) or get_first_order(client) is not None:
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


def get_wallet_balance(config, client):
    if config.WALLET_ENABLED:
        return get_balance(client.key.id())
    else:
        return 0


def get_points_balance(config, client):
    if config.PROMOS_API_KEY:
        return get_user_points(client.key.id())
    else:
        return 0


def get_text(module):
    text = module.text
    if module.type == NEW_USERS_WITH_NO_ORDERS and not module.already_sent:
        text += u"Скидка 50% на первый заказ истекает через 3 дня. Получите скидку сейчас."
    elif module.type == NEW_USERS_WITH_NO_ORDERS and module.already_sent:
        text += u"Скидка 50% на первый заказ продлена. Сделайте заказ сейчас."
    return text


def should_sms(config, module, client):
    wallet_balance = get_wallet_balance(config, client)
    points_balance = get_points_balance(config, client)

    if module.should_sms:
        return True
    elif module.sms_if_has_points and module.sms_if_has_cashback:
        return wallet_balance or points_balance
    elif module.sms_if_has_points:
        return points_balance
    elif module.sms_if_has_cashback:
        return wallet_balance
    return False


def should_push(config, module, client):
    return module.should_push


class NotificatingInactiveUsersHandler(RequestHandler):
    def apply_module(self, module):
        if not module or not module.status:
            return
        cnf = Config.get()
        all_clients = get_clients()
        clients = filter_clients_by_module_logic(module, all_clients)
        for client in clients:
            text = get_text(module)
            if not module.already_sent:
                module.already_sent = True
                if should_sms(cnf, module, client):
                    deferred.defer(send_sms, [client.tel], text)
                    ClientSmsSending(client=client.key, sms_type=module.type).put()
                    module.already_sent = True
                if should_push(cnf, module, client):
                    push = SimplePush(text=module.text, header=module.header, full_text=text, client=client,
                                      namespace=namespace_manager.get_namespace(), should_popup=True)

                    deferred.defer(push.send)
                    ClientPushSending(client=client.key, type=module.type).put()
            else:
                module.status = 0

    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            cnf = Config.get()
            if not cnf:
                continue
            for module in cnf.NOTIFICATING_INACTIVE_USERS_MODULE:
                self.apply_module(module)

            self.redirect_to('list_notif_modules')

# class SendSmsInactiveClientsHandler(RequestHandler):
#     @staticmethod
#     def get_clients_from_now(days):
#         namespace = namespace_manager.get_namespace()
#         namespace_manager.set_namespace('')  # query global clients
#         clients = Client.query(Client.created > datetime.now() - timedelta(days=days),
#                                Client.namespace_created == namespace).fetch()
#         namespace_manager.set_namespace(namespace)  # query clients in namespace
#         clients.extend(Client.query(Client.created > datetime.now() - timedelta(days=days)).fetch())
#         return clients
#
#     @staticmethod
#     def get_clients_from_orders_in_period(start_from, end_from):
#         start = datetime.utcnow() - timedelta(days=start_from)
#         end = datetime.utcnow() - timedelta(days=end_from)
#         orders = Order.query(Order.date_created > start, Order.date_created < end).fetch()
#         clients = set([order.client_id for order in orders
#                        if Order.query(Order.client_id == order.client_id).order(
#                 -Order.date_created).get().date_created == order.date_created])
#         return [Client.get(client) for client in clients]
#
#     @staticmethod
#     def get_wallet_balance(config, client):
#         if config.WALLET_ENABLED:
#             return get_balance(client.key.id())
#         else:
#             return 0
#
#     @staticmethod
#     def get_points_balance(config, client):
#         if config.PROMOS_API_KEY:
#             return get_user_points(client.key.id())
#         else:
#             return 0
#
#     @staticmethod
#     def filter_client_by_module_logic(module, clients):
#         new_clients = []
#         for client in clients[:]:
#             if module.type == REPEATED_ORDER_CONDITIONS:
#                 condition = PromoCondition(method=PromoCondition.CHECK_REPEATED_ORDERS, value=module.days)
#                 if not check_repeated_order_before(condition, client):
#                     continue
#             if module.type == REPEATED_ORDER_ONE_USE_CONDITION:
#                 condition = PromoCondition(method=PromoCondition.CHECK_REPEATED_ORDERS, value=module.days)
#                 if not check_repeated_order_before(condition, client):
#                     continue
#                 condition = PromoCondition(method=PromoCondition.CHECK_MAX_USES, value=1)
#                 if not check_max_promo_uses(condition, client):
#                     continue
#             new_clients.append(client)
#         return new_clients
#
#     @staticmethod
#     def unworthy_send_sms(client, module, wallet_balance, point_balance):
#         if not client.tel:
#             return True
#         for sending in ClientSmsSending.query(ClientSmsSending.client == client.key,
#                                               ClientSmsSending.sms_type == module.type).fetch():
#             if sending.created > datetime.utcnow() - timedelta(days=module.last_sms):
#                 return True
#         if not wallet_balance and module.only_with_cash_back:
#             return True
#         if not point_balance and module.only_with_points:
#             return True
#         return False
#
#     @staticmethod
#     def unworthy_send_push(client, module):
#         now = datetime.utcnow()
#         now = datetime.combine(now, time(hour=0, minute=0))
#         for sending in ClientSmsSending.query(ClientSmsSending.client == client.key,
#                                               ClientSmsSending.sms_type == module.type).fetch():
#             if sending.created > now:
#                 return True
#         for sending in ClientPushSending.query(ClientPushSending.client == client.key,
#                                                ClientPushSending.type == module.type).fetch():
#             if sending.created > now:
#                 return True
#         return False
#
#     @staticmethod
#     def get_text(module, wallet_balance, point_balance):
#         text = module.text
#         if wallet_balance:
#             text += ' На Вашем Личном счете: %s.' % int(wallet_balance / 100.0)
#         if point_balance:
#             text += ' Вы уже накопили %s баллов.' % point_balance
#         return text
#
#     def apply_module(self, module):
#         if not module or not module.status:
#             return
#         config = Config.get()
#
#         if module.type == ORDER_IN_ONE_DAY:
#             clients = self.get_clients_from_orders_in_period(module.days + 1, module.days)
#         else:
#             clients = self.get_clients_from_now(module.days)
#         for client in clients:
#             clients = self.filter_client_by_module_logic(module, clients)
#
#             wallet_balance = self.get_wallet_balance(config, client)
#             point_balance = self.get_points_balance(config, client)
#
#             text = self.get_text(module, wallet_balance, point_balance)
#             if not self.unworthy_send_sms(client, module, wallet_balance, point_balance):
#                 deferred.defer(send_sms, [client.tel], text)
#                 ClientSmsSending(client=client.key, sms_type=module.type).put()
#             else:
#                 if not self.unworthy_send_push(client, module):
#                     deferred.defer(send_client_push, client, text, module.header, namespace_manager.get_namespace())
#                     ClientPushSending(client=client.key, type=module.type).put()
#
#     def get(self):
#         for namespace in metadata.get_namespaces():
#             namespace_manager.set_namespace(namespace)
#             config = Config.get()
#             for module in config.SENDING_SMS_MODULE:
#                 self.apply_module(module)
