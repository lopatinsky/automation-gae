# coding: utf-8

__author__ = 'dvpermyakov'

from webapp2 import RequestHandler
from models import Client, PromoCondition
from models.config.config import Config
from datetime import datetime, timedelta
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from methods.orders.promos import check_repeated_order_before, check_max_promo_uses
from methods.sms.sms_pilot import send_sms
from models.config.inactive_clients import REPEATED_ORDER_CONDITIONS, REPEATED_ORDER_ONE_USE_CONDITION
from models.specials import ClientSmsSending


class SendSmsInactiveClientsHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            module = config.SENDING_SMS_MODULE
            if not module or not module.status:
                continue
            for client in Client.query(Client.created > datetime.now() - timedelta(days=module.days)).fetch():
                if not client.tel:
                    continue
                if ClientSmsSending.query(ClientSmsSending.client == client.key,
                                          ClientSmsSending.sms_type == module.type).get():
                    continue
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
                ClientSmsSending(client=client.key, sms_type=module.type).put()
                deferred.defer(send_sms, [client.tel], module.text)
