from google.appengine.ext import ndb
from handlers.api.base import ApiHandler
from models import Venue

__author__ = 'ilyazorin'


class VenuesHandler(ApiHandler):
    def get(self):
        venues = Venue.query(Venue.active == True).fetch()
        location = self.request.get("ll")
        try:
            location = ndb.GeoPt(location)
        except ValueError:
            location = None

        venue_dicts = [venue.dict(location) for venue in venues]
        if location:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['distance'])
        else:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['address'])
        self.render_json({'venues': venue_dicts})
