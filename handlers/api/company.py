from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from base import ApiHandler
from config import config, Config
from models import STATUS_AVAILABLE, Venue
from models.venue import DELIVERY
from models.specials import get_channels

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
                    for zone in sorted([zone_key.get() for zone_key in venue_delivery.delivery_zones],
                                       key=lambda zone: zone.sequence_number):
                        if zone.key not in zones:
                            zones[zone.key] = zone
        cities = []
        for zone in zones.values():
            if zone.address.city not in cities:
                cities.append(zone.address.city)
        self.render_json({
            'app_name': config.APP_NAME,
            'description': config.COMPANY_DESCRIPTION,
            'delivery_types': deliveries.values(),
            'cities': cities,
            'phone': config.SUPPORT_PHONE,
            'site': config.SUPPORT_SITE,
            'emails': config.SUPPORT_EMAILS,
            'screen_logic_type': config.SCREEN_LOGIC,
            'push_channels': get_channels(namespace_manager.get_namespace())
        })


class CompanyBaseUrlsHandler(ApiHandler):
    def get(self):
        companies = []
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            if config and config.APP_NAME:
                companies.append({
                    'base_url': u'http://%s.test.%s' % (namespace, urlparse(self.request.url).hostname),
                    'app_name': config.APP_NAME
                })
        self.render_json({
            'companies': companies
        })