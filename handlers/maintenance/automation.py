# coding:utf-8
from urlparse import urlparse
from google.appengine.ext.ndb import metadata
from models import DeliverySlot, Venue, MenuCategory

__author__ = 'dvpermyakov'

from base import BaseHandler


class CompaniesListHandler(BaseHandler):
    def get(self):
        self.render('/companies.html', **{
            'companies': metadata.get_namespaces()
        })

    def post(self):
        url = u'http://%s.1.%s/mt/report' % (self.request.get('company'), urlparse(self.request.url).hostname)
        self.redirect(str(url))