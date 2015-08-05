import datetime

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from config import Config
from methods.emails import admins
from models import SharedGift

MAX_DAYS_BEFORE_CANCEL = 7


class CancelGiftsHandler(RequestHandler):
    def get(self):
        time = datetime.datetime.now() - datetime.timedelta(days=MAX_DAYS_BEFORE_CANCEL)
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            unused_gifts = SharedGift.query(SharedGift.status == SharedGift.READY)
            old_gifts = [g for g in unused_gifts if g.created < time]
            if old_gifts:
                admins.send_error("order",
                                 "Unused gifts found", "Gifts not used within 7 days: %s. In company %s" % (len(old_gifts), config.APP_NAME))
                for gift in old_gifts:
                    gift.cancel()