# coding:utf-8
from urlparse import urlparse
from google.appengine.ext.ndb import metadata
from models import DeliverySlot, Venue, MenuCategory

__author__ = 'dvpermyakov'

from base import BaseHandler


class CompaniesListHandler(BaseHandler):
    def get(self):
        '''
        d1 = DeliverySlot(name=u'Сейчас', slot_type=0, value=0).put()
        d2 = DeliverySlot(name=u'Через 5 минут', slot_type=0, value=5).put()
        d3 = DeliverySlot(name=u'Через 10 минут', slot_type=0, value=10).put()
        d4 = DeliverySlot(name=u'Через 15 минут', slot_type=0, value=15).put()
        d5 = DeliverySlot(name=u'Через 20 минут', slot_type=0, value=20).put()
        d6 = DeliverySlot(name=u'Через 25 минут', slot_type=0, value=25).put()
        d7 = DeliverySlot(name=u'Через 30 минут', slot_type=0, value=30).put()
        for venue in Venue.query(Venue.active == True).fetch():
            for delivery in venue.delivery_types:
                if delivery.delivery_type in [0, 1]:
                    delivery.max_time = 86400
                    delivery.delivery_slots = [d1, d2, d3, d4, d5, d6, d7]
                if delivery.delivery_type == 2:
                    delivery.min_time = 3600
            venue.put()'''
        self.render('/companies.html', **{
            'companies': metadata.get_namespaces()
        })

    def post(self):
        url = u'http://%s.1.%s/mt/report' % (self.request.get('company'), urlparse(self.request.url).hostname)
        self.redirect(str(url))