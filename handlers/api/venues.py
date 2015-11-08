from handlers.api.base import ApiHandler
from methods.rendering import get_location
from models import Venue, STATUS_AVAILABLE
from models.venue import SELF, IN_CAFE, PICKUP

__author__ = 'ilyazorin'


class VenuesHandler(ApiHandler):
    def get(self):
        venues = Venue.fetch_venues(Venue.active == True)
        location = get_location(self.request.get("ll"))

        venue_dicts = []
        for venue in venues:
            for delivery in venue.delivery_types:
                if delivery.status == STATUS_AVAILABLE and delivery.delivery_type in [SELF, IN_CAFE, PICKUP]:
                    venue_dicts.append(venue.dict(location))
                    break
        if location:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['distance'])
        else:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['address'])
        self.render_json({'venues': venue_dicts})
