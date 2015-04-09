from google.appengine.ext import ndb
from base import BaseHandler
from models import Venue, MenuItem


class CreateVenueHandler(BaseHandler):
    def get(self):
        self.render('edit_venue.html')

    def post(self):
        venue = Venue()
        raw_params = ('title', 'description', 'working_days', 'working_hours', 'holiday_schedule', 'problem')
        for param in raw_params:
            setattr(venue, param, self.request.get(param))
        venue.coordinates = ndb.GeoPt(self.request.get('coordinates'))
        venue.phone_numbers = [n.strip() for n in self.request.get('phone_numbers').split(',')]
        venue.put()
        self.redirect('/mt/venues')


class EnableVenuesHandler(BaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        self.render('enable_venues.html', venues=venues)

    def post(self):
        venues = Venue.query().fetch()
        for v in venues:
            venue_id = str(v.key.id())
            new_active = bool(self.request.get(venue_id))
            if v.active != new_active:
                v.active = new_active
                v.put()
        self.render('enable_venues.html', venues=venues, success=True)


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

        raw_params = ('title', 'description', 'working_days', 'working_hours', 'holiday_schedule', 'problem')
        for param in raw_params:
            setattr(venue, param, self.request.get(param))

        venue.coordinates = ndb.GeoPt(self.request.get('coordinates'))
        venue.phone_numbers = [n.strip() for n in self.request.get('phone_numbers').split(',')]

        venue.put()
        self.render('edit_venue.html', venue=venue, success=True)


class VenueListHandler(BaseHandler):
    def get(self):
        self.render('menu/venue_list.html', **{
            'venues': Venue.query().fetch()
        })


class AddRestrictionHandler(BaseHandler):
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue_key = ndb.Key('Venue', venue_id)
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        products = MenuItem.query().fetch()
        for product in products:
            if venue_key in product.restrictions:
                product.avail = False
            else:
                product.avail = True
        self.render('menu/select_products_restriction.html', **{
            'products': products,
            'venue': venue
        })

    def post(self):
        venue_id = self.request.get_range('venue_id')
        venue_key = ndb.Key('Venue', venue_id)
        for product in MenuItem.query().fetch():
            confirmed = bool(self.request.get(str(product.key.id())))
            if venue_key in product.restrictions:
                if confirmed:
                    product.restrictions.remove(venue_key)
                    product.put()
            else:
                if not confirmed:
                    product.restrictions.append(venue_key)
                    product.put()
        self.redirect_to('venues_list')