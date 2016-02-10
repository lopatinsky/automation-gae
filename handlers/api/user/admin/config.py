from .base import AdminApiHandler
from methods.auth import api_admin_required
from models import STATUS_AVAILABLE
from models.config.config import config
from models.venue import Venue


def _get_delivery_types(venue):
    if venue:
        deliveries = [dt.delivery_type for dt in venue.delivery_types if dt.status == STATUS_AVAILABLE]
    else:
        deliveries = [venue_delivery.delivery_type
                      for venue in Venue.fetch_venues()
                      if venue.active
                      for venue_delivery in venue.delivery_types
                      if venue_delivery.status == STATUS_AVAILABLE]
        deliveries = list(set(deliveries))
    return deliveries


def _get_config(admin):
    venue = admin.venue.get() if admin.venue else None
    active_venues = Venue.query(Venue.active == True).fetch()
    return {
        'venue': venue.dict() if venue else None,
        'login': admin.login,
        'app_name': config.APP_NAME,
        'app_kind': config.APP_KIND,
        'delivery_types': _get_delivery_types(venue),
        'venues': [v.dict() for v in active_venues],
        'venue_id': admin.venue.id() if admin.venue else None,
        'google_analytics_api_key_ios': config.GOOGLE_ANALYTICS_API_KEY_IOS,
        'google_analytics_api_key_android': config.GOOGLE_ANALYTICS_API_KEY_ANDROID
    }


class ConfigHandler(AdminApiHandler):
    @api_admin_required
    def get(self):
        self.render_json(_get_config(self.user))
