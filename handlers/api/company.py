from base import ApiHandler
from config import config
from models import DeliveryType, DELIVERY_MAP, STATUS_AVAILABLE, Venue

__author__ = 'dvpermyakov'


class CompanyInfoHandler(ApiHandler):
    def get(self):
        cities = []
        for venue in Venue.query(Venue.active == True).fetch():
            if venue.address.city not in cities:
                cities.append(venue.address.city)
        self.render_json({
            'app_name': config.APP_NAME,
            'description': config.COMPANY_DESCRIPTION,
            'delivery_types': [{
                'id': delivery.delivery_type,
                'name': DELIVERY_MAP[delivery.delivery_type],
                'min_sum': delivery.min_sum,
            } for delivery in DeliveryType.query(DeliveryType.status == STATUS_AVAILABLE).fetch()],
            'cities': cities,
            'phone': config.SUPPORT_PHONE,
            'site': config.SUPPORT_SITE,
            'emails': config.SUPPORT_EMAILS
        })