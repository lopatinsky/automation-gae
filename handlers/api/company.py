from urlparse import urlparse

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata

from base import ApiHandler
from models.config.config import config, Config
from methods.versions import is_available_version, get_version
from models import STATUS_AVAILABLE, Venue, Client
from models.proxy.resto import RestoCompany
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
            'promo_code_active': PromoCode.query(PromoCode.status.IN(PROMO_CODE_ACTIVE_STATUS_CHOICES)).get() is not None,
            'delivery_types': deliveries.values(),
            'cities': cities,
            'screen_logic_type': config.SCREEN_LOGIC,
            'push_channels': get_channels(namespace_manager.get_namespace()),
            'colors': {
                'action': config.ACTION_COLOR,
            },
            'wallet': {
                'enabled': config.WALLET_ENABLED,
            },
            'share_gift': {
                'enabled': config.SHARE_GIFT_ENABLED,
            },
            'share_invitation': {
                'enabled': config.SHARE_INVITATION_ENABLED,
            },
            'new_version_popup': {
                'show': not is_available_version(self.request.headers.get('Version', 0)),
                'version': get_version(self.request.headers.get('Version', 0)).dict()
            },
            'cancel_order': RestoCompany.get() is not None,
            'back_end': config.APP_KIND
        }
        response.update(config.get_company_dict())
        self.render_json(response)


class CompanyModulesHandler(ApiHandler):
    def get(self):
        client_id = int(self.request.headers.get('Client-Id') or 0)
        if client_id:
            client = Client.get_by_id(client_id)
        else:
            client = None
        modules = []
        if config.SUBSCRIPTION_MODULE and config.SUBSCRIPTION_MODULE.status:
            modules.append(config.SUBSCRIPTION_MODULE.dict())
        if config.SHARE_GIFT_MODULE and config.SHARE_GIFT_MODULE.status:
            modules.append(config.SHARE_GIFT_MODULE.dict())
        if config.SHARE_INVITATION_MODULE and config.SHARE_INVITATION_MODULE.status:
            modules.append(config.SHARE_INVITATION_MODULE.dict())
        if config.CLIENT_MODULE and config.CLIENT_MODULE.status:
            modules.append(config.CLIENT_MODULE.dict())
        if config.ORDER_MODULE and config.ORDER_MODULE.status:
            modules.append(config.ORDER_MODULE.dict())
        if config.GEO_PUSH_MODULE and config.GEO_PUSH_MODULE.status:
            modules.append(config.GEO_PUSH_MODULE.dict(client))
        self.render_json({
            'modules': modules
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
