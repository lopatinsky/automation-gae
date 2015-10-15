import logging
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.deferred import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from methods.proxy.resto.menu import reload_menu
from models.proxy.resto import RestoCompany

__author__ = 'dvpermyakov'


def save_menu(namespace):
    logging.info(namespace)
    namespace_manager.set_namespace(namespace)
    resto_company = RestoCompany.get()
    if resto_company:
        reload_menu()
    else:
        logging.warning('Not found resto company')


class UpdateRestoHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            resto_company = RestoCompany.get()
            if resto_company:
                deferred.defer(save_menu, namespace)
