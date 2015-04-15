from urlparse import urlparse
from google.appengine.ext.ndb import metadata

__author__ = 'dvpermyakov'

from base import BaseHandler


class AutomationMainHandler(BaseHandler):
    def get(self):
        self.render('/automation.html')


class CompaniesListHandler(BaseHandler):
    def get(self):
        self.render('/companies.html', **{
            'companies': metadata.get_namespaces()
        })

    def post(self):
        url = u'http://%s.1.%s/mt/automation' % (self.request.get('company'), urlparse(self.request.url).hostname)
        self.redirect(str(url))