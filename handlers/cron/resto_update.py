from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from models import MenuCategory
from models.proxy.resto import RestoCompany

__author__ = 'dvpermyakov'


class UpdateRestoHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            resto_company = RestoCompany.query().get()
            if resto_company:
                deferred.defer(MenuCategory.get_menu_dict)