import datetime

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from models.config.config import Config
from methods.emails import admins
from models import SharedGift

MAX_DAYS_BEFORE_CANCEL = 7


class CancelGiftsHandler(RequestHandler):
    def get(self):
        time = datetime.datetime.now() - datetime.timedelta(days=MAX_DAYS_BEFORE_CANCEL)
        namespace_cancels = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            unused_gifts = SharedGift.query(SharedGift.status == SharedGift.READY)
            old_gifts = [gift for gift in unused_gifts if gift.created < time]
            if old_gifts:
                for gift in old_gifts:
                    gift.cancel(namespace)
                namespace_cancels[namespace] = 'Gifts not used within %s days: %s. In company %s\n' % \
                                               (MAX_DAYS_BEFORE_CANCEL, len(old_gifts), config.APP_NAME)
        if namespace_cancels:
            namespace_manager.set_namespace('')
            admins.send_error('order', 'Unused gifts found', ''.join(namespace_cancels.values()))