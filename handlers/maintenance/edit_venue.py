from google.appengine.ext import ndb
from .base import BaseHandler
from models import Venue


class EditVenueHandler(BaseHandler):
    def get(self, venue_id):
        venue = Venue.get_by_id(int(venue_id))
        if not venue:
            self.abort(404)
        self.render('edit_venue.html', venue=venue)

    def post(self, venue_id):
        venue = Venue.get_by_id(int(venue_id))
        if not venue:
            self.abort(404)

        raw_params = ('title', 'description', 'working_days', 'working_hours', 'holiday_schedule')
        for param in raw_params:
            setattr(venue, param, self.request.get(param))

        venue.coordinates = ndb.GeoPt(self.request.get('coordinates'))
        venue.phone_numbers = [n.strip() for n in self.request.get('phone_numbers').split(',')]

        venue.put()
        self.render('edit_venue.html', venue=venue, success=True)
