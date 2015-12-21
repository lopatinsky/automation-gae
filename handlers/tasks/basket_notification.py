import logging
from datetime import datetime, date, time

from google.appengine.api.namespace_manager import namespace_manager

from webapp2 import RequestHandler

from models import Client, STATUS_AVAILABLE
from models.config.config import Config
from models.geo_push import LeftBasketPromo
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
            conf = Config.get()
            module = conf.BASKET_NOTIFICATION_MODULE

            push = SimplePush(text=module.text, header=module.header, full_text=module.text, should_popup=False,
                              client=client, namespace=namespace)
            push.send()
            LeftBasketPromo(client=client.key).put()

        client.notif_id = None
        client.put()
