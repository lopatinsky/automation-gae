from .base import BaseHandler
from models import Venue


class EnableVenuesHandler(BaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        self.render('mt/enable_venues.html', venues=venues)

    def post(self):
        venues = Venue.query().fetch()
        for v in venues:
            venue_id = str(v.key.id())
            new_active = bool(self.request.get(venue_id))
            if v.active != new_active:
                v.active = new_active
                v.put()
        self.render('mt/enable_venues.html', venues=venues, success=True)
