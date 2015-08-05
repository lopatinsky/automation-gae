# coding:utf-8
from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from config import Config
from models.proxy.resto import RestoCompany

__author__ = 'dvpermyakov'

from base import BaseHandler


class CompaniesListHandler(BaseHandler):
    def get(self):
        namespace_manager.set_namespace('sushilar')
        config = Config.get()
        config.RESTO_COMPANY = RestoCompany.get_by_id(5725202142986240).key
        config.put()
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
        url = u'http://%s.1.%s/mt/report' % (self.request.get('company'), urlparse(self.request.url).hostname)
        self.redirect(str(url))