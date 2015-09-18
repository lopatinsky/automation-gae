from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from models.config.config import Config
from methods.emails import admins
from models.specials import Subscription


class CloseSubscriptionHandler(RequestHandler):
    def get(self):
        namespace_subscription = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            now = datetime.utcnow()
            subscription_number = Subscription.query(Subscription.expiration < now).count()
            text = 'Subscription count = %s are expired. In company %s\n' % (subscription_number, config.APP_NAME)
            namespace_subscription[namespace] = text
        if namespace_subscription:
            admins.send_error('subscription', 'Subscriptions are expired', ''.join(namespace_subscription.values()))
