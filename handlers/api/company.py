from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from base import ApiHandler
from config import config, Config
from models import STATUS_AVAILABLE, Venue
from models.venue import DELIVERY
from models.specials import COMPANY_CHANNEL, VENUE_CHANNEL, CLIENT_CHANNEL, ORDER_CHANNEL

__author__ = 'dvpermyakov'


class CompanyInfoHandler(ApiHandler):
    def get(self):
        zones = {}
        deliveries = {}
        for venue in Venue.query(Venue.active == True).fetch():
            for venue_delivery in venue.delivery_types:
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type not in deliveries:
                    deliveries[venue_delivery.delivery_type] = venue_delivery.dict()
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type == DELIVERY:
                    for zone in venue_delivery.delivery_zones:
                        if zone not in zones:
                            zones[zone] = zone.get()
        cities = []
        for zone in zones.values():
            cities.append(zone.address.city)
        self.render_json({
            'app_name': config.APP_NAME,
            'description': config.COMPANY_DESCRIPTION,
            'delivery_types': deliveries.values(),
            'cities': cities,
            'phone': config.SUPPORT_PHONE,
            'site': config.SUPPORT_SITE,
            'emails': config.SUPPORT_EMAILS,
            'push_channels': {
                'company': COMPANY_CHANNEL,
                'venue': VENUE_CHANNEL,
                'client': CLIENT_CHANNEL,
                'order': ORDER_CHANNEL
            }
        })


class CompanyBaseUrlsHandler(ApiHandler):
    def get(self):
        companies = []
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            companies.append({
                'base_url': u'http://%s.1.%s' % (namespace, urlparse(self.request.url).hostname),
                'app_name': Config.get().APP_NAME
            })
        self.render_json({
            'companies': companies
        })