# coding:utf-8
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata

from models.config.config import Config
from models.config.version import CURRENT_VERSION, CURRENT_APP_ID
from models.proxy.doubleb import DoublebCompany

__author__ = 'dvpermyakov'

from base import BaseHandler


class CompaniesListHandler(BaseHandler):
    def get(self):
        namespace_manager.set_namespace('doubleb')
        DoublebCompany(test_server=True).put()
        namespaces = []
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            if config:
                namespaces.append(namespace)
        self.render('/companies.html', **{
            'companies': namespaces
        })

    def post(self):
        url = u'http://%s.%s.%s.appspot.com/mt/report' % (
            self.request.get('company'), CURRENT_VERSION, CURRENT_APP_ID)
        self.redirect(str(url))