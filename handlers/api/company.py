from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from base import ApiHandler
from config import config, Config
from methods.rendering import latinize
from methods.versions import is_available_version, get_version
from models import STATUS_AVAILABLE, Venue
from models.venue import DELIVERY
from models.specials import get_channels
from models.promo_code import PromoCode, PROMO_CODE_ACTIVE_STATUS_CHOICES

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
                        zone = zone.get()
                        if zone.status == STATUS_AVAILABLE and zone.key not in zones:
                            zones[zone.key] = zone
        cities = []
        for zone in sorted(zones.values(), key=lambda zone: zone.sequence_number):
            if zone.address.city not in cities:
                cities.append(zone.address.city)
        self.render_json({
            'extra_client_fields': [{
                'fields': [{
                    'title': field,
                    'field': latinize(field),
                    'type': 'string'
                } for field in config.EXTRA_CLIENT_INFO_FIELDS],
                'module': None,
                'group': 0
            }],
            'app_name': config.APP_NAME,
            'promo_code_active': PromoCode.query(PromoCode.status.IN(PROMO_CODE_ACTIVE_STATUS_CHOICES)).get() is not None,
            'description': config.COMPANY_DESCRIPTION,
            'delivery_types': deliveries.values(),
            'cities': cities,
            'phone': config.SUPPORT_PHONE,
            'site': config.SUPPORT_SITE,
            'emails': config.SUPPORT_EMAILS,
            'screen_logic_type': config.SCREEN_LOGIC,
            'push_channels': get_channels(namespace_manager.get_namespace()),
            'colors': {
                'action': config.ACTION_COLOR,
            },
            'share_gift': {
                'enabled': config.SHARED_GIFT_ENABLED,
            },
            'share_invitation': {
                'enabled': config.SHARED_INVITATION_ENABLED,
            },
            'new_version_popup': {
                'show': not is_available_version(self.request.headers.get('Version', 0)),
                'version': get_version(self.request.headers.get('Version', 0)).dict()
            }
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