from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from models import STATUS_AVAILABLE
from models.config.config import Config
from methods.emails import admins
from models.subscription import Subscription


class CloseSubscriptionHandler(RequestHandler):
    def get(self):
        namespace_subscription = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            now = datetime.utcnow()
            subscriptions = Subscription.query(Subscription.expiration < now,
                                               Subscription.status == STATUS_AVAILABLE).fetch()
            for subscription in subscriptions:
                subscription.close()
            if len(subscriptions) > 0:
                text = 'Subscription count = %s are expired. In company %s\n' % (len(subscriptions), namespace)
                namespace_subscription[namespace] = text
        if namespace_subscription:
            namespace_manager.set_namespace('')
            admins.send_error('subscription', 'Subscriptions are expired', ''.join(namespace_subscription.values()))
