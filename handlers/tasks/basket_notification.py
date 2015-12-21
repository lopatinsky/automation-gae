import logging
from google.appengine.api.namespace_manager import namespace_manager

from webapp2 import RequestHandler

from models import Client
from models.config import config
from models.push import SimplePush

__author__ = 'Artem'


class BasketNotificationHandler(RequestHandler):
    def post(self):
        conf = config.Config.get()
        module = conf.BASKET_NOTIFICATION_MODULE
        client_id = self.request.get_range('client_id')
        namespace = self.request.get('namespace')
        namespace_manager.set_namespace(namespace)
        client = Client.get(client_id)
        logging.debug(client)

        if module and module.status:
            push = SimplePush(text=module.text, header=module.header, full_text=module.text, should_popup=False,
                              client=client, namespace=namespace)
            push.send()
