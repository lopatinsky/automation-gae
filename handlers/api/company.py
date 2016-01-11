# coding=utf-8
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata

from base import ApiHandler
from methods.cities import get_company_cities
from methods.fuckups import fuckup_ios_delivery_types
from models.config.config import config, Config
from methods.versions import is_available_version, get_version
from models import Venue, Client, STATUS_UNAVAILABLE, DeliveryZone, STATUS_AVAILABLE
from models.config.menu import RemaindersModule
from models.config.version import CURRENT_APP_ID, CURRENT_VERSION
from models.proxy.resto import RestoCompany
from models.proxy.unified_app import AutomationCompany
from models.venue import DELIVERY
from models.specials import get_channels
from models.promo_code import PromoCode, PROMO_CODE_ACTIVE_STATUS_CHOICES

__author__ = 'dvpermyakov'


class AppConfigurationHandler(ApiHandler):
    def get(self):
        has_cities = bool(get_company_cities())
        has_companies = AutomationCompany.query().get(keys_only=True) is not None

        self.render_json({
            'has_cities': has_cities,
            'has_companies': has_companies,

            'keys': {
                'branch': config.BRANCH_API_KEY,
                'parse': {
                    'app_key': config.PARSE_APP_API_KEY,
                    'client_key': config.PARSE_CLIENT_API_KEY,
                }
            }
        })


class CompanyInfoHandler(ApiHandler):
    def get(self):
        zones = set()
        deliveries = {}
        for venue in Venue.fetch_venues(Venue.active == True):
            for venue_delivery in venue.delivery_types:
                if venue_delivery.status == STATUS_UNAVAILABLE:
                    continue
                if venue_delivery.delivery_type not in deliveries:
                    deliveries[venue_delivery.delivery_type] = venue_delivery.dict()
                if venue_delivery.delivery_type == DELIVERY:
                    zones.update(venue_delivery.delivery_zones)
        deliveries = fuckup_ios_delivery_types(deliveries.values())
        cities = []
        for zone in sorted([DeliveryZone.get(zone) for zone in list(zones)], key=lambda zone: zone.sequence_number):
            if zone.address.city not in cities:
                cities.append(zone.address.city)
        if config.ANOTHER_CITY_IN_LIST:
            cities.append(u'Другой город')
        version = get_version(self.request.headers.get('Version', 0))
        response = {
            'promo_code_active': PromoCode.query(PromoCode.status.IN(PROMO_CODE_ACTIVE_STATUS_CHOICES)).get() is not None,
            'delivery_types': deliveries,
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
                'enabled': config.SHARE_GIFT_ENABLED or (config.MIVAKO_GIFT_MODULE is not None and
                                                         config.MIVAKO_GIFT_MODULE.status == STATUS_AVAILABLE)
            },
            'share_invitation': {
                'enabled': config.SHARE_INVITATION_ENABLED,
            },
            'new_version_popup': {
                'show': not is_available_version(self.request.headers.get('Version', 0)),
                'version': version.dict() if version else None
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
            client = Client.get(client_id)
        else:
            client = None
        modules = []
        if config.SUBSCRIPTION_MODULE and config.SUBSCRIPTION_MODULE.status:
            modules.append(config.SUBSCRIPTION_MODULE.dict())
        if config.SHARE_GIFT_MODULE and config.SHARE_GIFT_MODULE.status:
            modules.append(config.SHARE_GIFT_MODULE.dict())
        if config.SHARE_INVITATION_ENABLED:
            modules.append(config.SHARE_INVITATION_MODULE.dict())
        if config.CLIENT_MODULE and config.CLIENT_MODULE.status:
            modules.append(config.CLIENT_MODULE.dict())
        if config.ORDER_MODULE and config.ORDER_MODULE.status:
            modules.extend(config.ORDER_MODULE.dicts())
        if config.GEO_PUSH_MODULE and config.GEO_PUSH_MODULE.status:
            modules.append(config.GEO_PUSH_MODULE.dict(client))
        if config.MIVAKO_GIFT_MODULE and config.MIVAKO_GIFT_MODULE.status:
            modules.append(config.MIVAKO_GIFT_MODULE.dict())
        if RemaindersModule.has_module():
            modules.append(config.REMAINDERS_MODULE.dict())
        self.render_json({
            'modules': modules
        })


class CompanyBaseUrlsHandler(ApiHandler):
    def get(self):
        companies = []
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            if config and config.APP_NAME:
                companies.append({
                    'base_url': u'http://%s.%s.%s.appspot.com' % (namespace, CURRENT_VERSION, CURRENT_APP_ID),
                    'app_name': config.APP_NAME
                })
        self.render_json({
            'companies': companies
        })
