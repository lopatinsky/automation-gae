from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from methods.emails import admins
from methods.hit import update_ratings, update_hit_category
from models import STATUS_AVAILABLE
from models.config.config import Config

__author__ = 'dvpermyakov'


class UpdateRatingHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            if config.HIT_MODULE and config.HIT_MODULE.status == STATUS_AVAILABLE:
                deferred.defer(update_ratings)


class UpdateHitCategoryHandler(RequestHandler):
    def get(self):
        namespace_hit = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            if config.HIT_MODULE and config.HIT_MODULE.status == STATUS_AVAILABLE:
                module = config.HIT_MODULE
                update_hit_category()
                items_str = u'\n'.join(['%s: rating = %s' % (item.get().title, round(item.get().rating, 3))
                                        for item in module.items])
                text = 'In company (%s), hit category (%s) has items: \n%s\n\n' % (config.APP_NAME, module.title, items_str)
                namespace_hit[namespace] = text
        if namespace_hit:
            namespace_manager.set_namespace('')
            admins.send_error('hits', 'Hits has been changed', ''.join(namespace_hit.values()))
