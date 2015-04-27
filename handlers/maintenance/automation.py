# coding:utf-8
from urlparse import urlparse
from google.appengine.ext.ndb import metadata
from methods.rendering import latinize

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


class CreateCompanyHandler(BaseHandler):
    def get(self):
        self.render('create_company.html')

    def post(self):
        name = self.request.get('name')
        name = latinize(name)
        for metadata_instance in metadata.get_namespaces():
            if name == metadata_instance:
                return self.abort(400)
        url = u'http://%s.1.%s/mt/automation' % (name, urlparse(self.request.url).hostname)
        self.redirect(str(url))