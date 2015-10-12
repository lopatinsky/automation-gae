from google.appengine.api import memcache
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from models import MenuCategory
from models.proxy.resto import RestoCompany

__author__ = 'dvpermyakov'


def save_menu(namespace):
    namespace_manager.set_namespace(namespace)
    resto_company = RestoCompany.get()
    memcache.set('menu_%s' % resto_company.key.id(), None)
    menu = MenuCategory.get_menu_dict()
    memcache.set('menu_%s' % namespace, menu, time=24*3600)


class UpdateRestoHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            resto_company = RestoCompany.query().get()
            if resto_company:
                deferred.defer(save_menu, namespace)
