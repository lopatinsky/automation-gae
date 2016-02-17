import logging
from datetime import datetime, date, time, timedelta

from google.appengine.api.namespace_manager import namespace_manager

from webapp2 import RequestHandler

from models import Client
from models.config.config import config
from models.geo_push import LeftBasketPromo
from models.order import Order, NOT_CANCELED_STATUSES
from models.push import SimplePush

__author__ = 'Artem'


class BasketNotificationHandler(RequestHandler):
    def post(self):
        namespace = self.request.get('namespace')
        namespace_manager.set_namespace(namespace)

        client_id = self.request.get_range('client_id')
        client = Client.get(client_id)
        logging.debug(client)

        today = datetime.combine(date.today(), time())
        existing = LeftBasketPromo.query(LeftBasketPromo.client == client.key,
                                         LeftBasketPromo.created >= today).get()
        if not existing:
            module = config.BASKET_NOTIFICATION_MODULE

            send = True

            if module.days_since_order > 0:
                start_check_time = datetime.now() - timedelta(module.days_since_order)
                if Order.query(Order.client_id == client.key.id(),
                               Order.date_created >= start_check_time,
                               Order.status.IN(NOT_CANCELED_STATUSES)).get():
                    send = False

            if send:
                push = SimplePush(text=module.text, header=module.header, full_text=module.text, should_popup=False,
                                  client=client, namespace=namespace)
                push.send()
                LeftBasketPromo(client=client.key).put()

        client.notif_id = None
        client.put()
