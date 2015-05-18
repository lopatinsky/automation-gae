from base import ApiHandler
from config import config
from models import STATUS_AVAILABLE, Venue

__author__ = 'dvpermyakov'


class CompanyInfoHandler(ApiHandler):
    def get(self):
        cities = []
        deliveries = {}
        for venue in Venue.query(Venue.active == True).fetch():
            if venue.address.city not in cities:
                cities.append(venue.address.city)
            for venue_delivery in venue.delivery_types:
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type not in deliveries:
                    deliveries[venue_delivery.delivery_type] = venue_delivery.dict()
        self.render_json({
            'app_name': config.APP_NAME,
            'description': config.COMPANY_DESCRIPTION,
            'delivery_types': deliveries.values(),
            'cities': cities,
            'phone': config.SUPPORT_PHONE,
            'site': config.SUPPORT_SITE,
            'emails': config.SUPPORT_EMAILS
        })