from google.appengine.api.datastore_errors import BadValueError
from google.appengine.ext import ndb
from handlers.api.base import ApiHandler
from models import Venue, STATUS_AVAILABLE
from models.venue import SELF, IN_CAFE

__author__ = 'ilyazorin'


class VenuesHandler(ApiHandler):
    def get(self):
        venues = Venue.fetch_venues(self.app_kind, Venue.active == True)
        location = self.request.get("ll")
        try:
            location = ndb.GeoPt(location)
        except BadValueError:
            location = None

        venue_dicts = []
        for venue in venues:
            for delivery in venue.delivery_types:
                #if delivery.status == STATUS_AVAILABLE and delivery.delivery_type in [SELF, IN_CAFE]:
                if delivery.status == STATUS_AVAILABLE:
                    venue_dicts.append(venue.dict(location))
                    break
        if location:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['distance'])
        else:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['address'])
        self.render_json({'venues': venue_dicts})
