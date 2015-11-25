# coding: utf-8
from methods.empatika_promos import get_user_points
from methods.empatika_wallet import get_balance
from methods.push import send_client_push

__author__ = 'dvpermyakov'

from webapp2 import RequestHandler
from models import Client, PromoCondition, Order
from models.config.config import Config
from datetime import datetime, timedelta, time
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from methods.orders.promos import check_repeated_order_before, check_max_promo_uses
from methods.sms.sms_pilot import send_sms
from models.config.inactive_clients import REPEATED_ORDER_CONDITIONS, REPEATED_ORDER_ONE_USE_CONDITION, \
    ORDER_IN_ONE_DAY
from models.specials import ClientSmsSending, ClientPushSending


class SendSmsInactiveClientsHandler(RequestHandler):
    @staticmethod
    def get_clients_from_now(days):
        namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace('')  # query global clients
        clients = Client.query(Client.created > datetime.now() - timedelta(days=days),
                               Client.namespace_created == namespace).fetch()
        namespace_manager.set_namespace(namespace)  # query clients in namespace
        clients.extend(Client.query(Client.created > datetime.now() - timedelta(days=days)).fetch())
        return clients

    @staticmethod
    def get_clients_from_orders_in_period(start_from, end_from):
        start = datetime.utcnow() - timedelta(days=start_from)
        end = datetime.utcnow() - timedelta(days=end_from)
        orders = Order.query(Order.date_created > start, Order.date_created < end).fetch()
        clients = set([order.client_id for order in orders
                       if Order.query(Order.client_id == order.client_id).order(-Order.date_created).get().date_created == order.date_created])
        return [Client.get(client) for client in clients]

    @staticmethod
    def get_wallet_balance(config, client):
        if config.WALLET_ENABLED:
            return get_balance(client.key.id())
        else:
            return 0

    @staticmethod
    def get_points_balance(config, client):
        if config.PROMOS_API_KEY:
            return get_user_points(client.key.id())
        else:
            return 0

    @staticmethod
    def filter_client_by_module_logic(module, clients):
        new_clients = []
        for client in clients[:]:
            if module.type == REPEATED_ORDER_CONDITIONS:
                condition = PromoCondition(method=PromoCondition.CHECK_REPEATED_ORDERS, value=module.days)
                if not check_repeated_order_before(condition, client):
                    continue
            if module.type == REPEATED_ORDER_ONE_USE_CONDITION:
                condition = PromoCondition(method=PromoCondition.CHECK_REPEATED_ORDERS, value=module.days)
                if not check_repeated_order_before(condition, client):
                    continue
                condition = PromoCondition(method=PromoCondition.CHECK_MAX_USES, value=1)
                if not check_max_promo_uses(condition, client):
                    continue
            new_clients.append(client)
        return new_clients

    @staticmethod
    def unworthy_send_sms(client, module, wallet_balance, point_balance):
        if not client.tel:
            return True
        for sending in ClientSmsSending.query(ClientSmsSending.client == client.key,
                                              ClientSmsSending.sms_type == module.type).fetch():
            if sending.created > datetime.utcnow() - timedelta(days=module.last_sms):
                return True
        if not wallet_balance and module.only_with_cash_back:
            return True
        if not point_balance and module.only_with_points:
            return True
        return False

    @staticmethod
    def unworthy_send_push(client, module):
        now = datetime.utcnow()
        now = datetime.combine(now, time(hour=0, minute=0))
        for sending in ClientSmsSending.query(ClientSmsSending.client == client.key,
                                              ClientSmsSending.sms_type == module.type).fetch():
            if sending.created > now:
                return True
        for sending in ClientPushSending.query(ClientPushSending.client == client.key,
                                               ClientPushSending.type == module.type).fetch():
            if sending.created > now:
                return True
        return False

    @staticmethod
    def get_text(module, wallet_balance, point_balance):
        text = module.text
        if wallet_balance:
            text += ' На Вашем Личном счете: %s.' % int(wallet_balance / 100.0)
        if point_balance:
            text += ' Вы уже накопили %s баллов.' % point_balance
        return text

    def apply_module(self, module):
        if not module or not module.status:
            return
        config = Config.get()
        if module.type == ORDER_IN_ONE_DAY:
            clients = self.get_clients_from_orders_in_period(module.days + 1, module.days)
        else:
            clients = self.get_clients_from_now(module.days)
        for client in clients:
            clients = self.filter_client_by_module_logic(module, clients)

            wallet_balance = self.get_wallet_balance(config, client)
            point_balance = self.get_points_balance(config, client)

            text = self.get_text(module, wallet_balance, point_balance)
            if not self.unworthy_send_sms(client, module, wallet_balance, point_balance):
                deferred.defer(send_sms, [client.tel], text)
                ClientSmsSending(client=client.key, sms_type=module.type).put()
            else:
                if not self.unworthy_send_push(client, module):
                    deferred.defer(send_client_push, client, text, module.header, namespace_manager.get_namespace())
                    ClientPushSending(client=client.key, type=module.type).put()

    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            for module in config.SENDING_SMS_MODULE:
                self.apply_module(module)
