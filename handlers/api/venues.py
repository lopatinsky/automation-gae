from handlers.api.base import ApiHandler
from models import Venue

__author__ = 'ilyazorin'


class VenuesHandler(ApiHandler):

    #TODO check params
    def get(self):
        venues = Venue.query(Venue.active == True).fetch()
        location = self.request.get("ll")
        venue_dicts = [venue.dict(location) for venue in venues]
        if location:
            venue_dicts = sorted(venue_dicts, key=lambda v: v['distance'])
        self.render_json({'venues': venue_dicts})
