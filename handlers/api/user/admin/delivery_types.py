from handlers.api.user.admin.base import AdminApiHandler
from methods.auth import api_admin_required
from models import Venue, STATUS_AVAILABLE

__author__ = 'dvpermyakov'


class DeliveryTypesHandler(AdminApiHandler):
    @api_admin_required
    def get(self):
        deliveries = {}
        for venue in Venue.query(Venue.active == True).fetch():
            for venue_delivery in venue.delivery_types:
                if venue_delivery.status == STATUS_AVAILABLE and venue_delivery.delivery_type not in deliveries:
                    deliveries[venue_delivery.delivery_type] = venue_delivery.dict()
        self.render_json({
            'deliveries': deliveries.values()
        })