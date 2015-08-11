from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from base import ApiHandler
from config import config, Config
from methods.rendering import latinize
from models import STATUS_AVAILABLE, Venue
from models.venue import DELIVERY, DeliveryZone
from models.specials import get_channels
from models.promo_code import PromoCode, PROMO_CODE_ACTIVE_STATUS_CHOICES

__author__ = 'dvpermyakov'


class CompanyInfoHandler(ApiHandler):
    def get(self):
        zones = {}
        deliveries = {}
        for venue in Venue.fetch_venues(Venue.active == True):
            for venue_delivery in venue.delivery_types:
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type not in deliveries:
                    deliveries[venue_delivery.delivery_type] = venue_delivery.dict()
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type == DELIVERY:
                    for zone in venue_delivery.delivery_zones:
                        zone = DeliveryZone.get(zone)
                        if zone.status == STATUS_AVAILABLE and zone.key not in zones:
                            zones[zone.key] = zone
        cities = []
        for zone in sorted(zones.values(), key=lambda zone: zone.sequence_number):
            if zone.address.city not in cities:
                cities.append(zone.address.city)
        response = {
            'extra_client_fields': [{
                'fields': [{
                    'title': field,
                    'field': latinize(field),
                    'type': 'string'
                } for field in config.EXTRA_CLIENT_INFO_FIELDS],
                'module': None,
                'group': 0
            }],
            'promo_code_active': PromoCode.query(PromoCode.status.IN(PROMO_CODE_ACTIVE_STATUS_CHOICES)).get() is not None,
            'delivery_types': deliveries.values(),
            'cities': cities,
            'screen_logic_type': config.SCREEN_LOGIC,
            'push_channels': get_channels(namespace_manager.get_namespace()),
            'colors': {
                'action': config.ACTION_COLOR,
            },
        }
        response.update(config.get_company_dict())
        self.render_json(response)


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