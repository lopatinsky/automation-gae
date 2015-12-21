from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from models import STATUS_AVAILABLE
from models.geo_push import GeoPush, LeftBasketPromo


class CloseGeoPushesHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            for cls in (GeoPush, LeftBasketPromo):
                promos = cls.query(cls.status == STATUS_AVAILABLE).fetch()
                for promo in promos:
                    promo.deactivate()
