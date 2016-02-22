# coding=utf-8

from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from methods import push
from models import STATUS_AVAILABLE
from models.config.config import config
from methods.emails import admins
from models.subscription import Subscription


class CloseSubscriptionHandler(RequestHandler):
    def get(self):
        now = datetime.utcnow()
        namespace_subscription = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)

            unused = Subscription.query(Subscription.status == STATUS_AVAILABLE,
                                        Subscription.used_cups == 0,
                                        Subscription.payment_return_time < now).fetch()
            for subscription in unused:
                subscription.revert_payment()
                push.send_client_push(
                        subscription.client.get(),
                        u"Вы не начали использовать Ваш абонемент. Денежные средства будут возвращены Вам на карту.",
                        config.APP_NAME,
                        namespace
                )

            expired = Subscription.query(Subscription.expiration < now,
                                         Subscription.status == STATUS_AVAILABLE).fetch()
            for subscription in expired:
                subscription.close()

            if expired or unused:
                text = '%s: expired %s, unused %s' % (namespace, len(expired), len(unused))
                namespace_subscription[namespace] = text
        if namespace_subscription:
            namespace_manager.set_namespace('')
            admins.send_error('subscription', 'Subscriptions are expired', '\n'.join(namespace_subscription.values()))
