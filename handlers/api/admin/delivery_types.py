from base import AdminApiHandler
from models import Venue, STATUS_AVAILABLE

__author__ = 'dvpermyakov'


class DeliveryTypesHandler(AdminApiHandler):
    def get(self):
        deliveries = {}
        for venue in Venue.query(Venue.active == True).fetch():
            for venue_delivery in venue.delivery_types:
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type not in deliveries:
                    deliveries[venue_delivery.delivery_type] = venue_delivery.dict()
        self.render_json({
            'deliveries': deliveries.values()
        })