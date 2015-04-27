# coding:utf-8
import logging
from google.appengine.ext import ndb
from base import CompanyBaseHandler
from models import Venue, MenuItem, MenuCategory, STATUS_AVAILABLE
from methods import map


class CreateVenueHandler(CompanyBaseHandler):
    def get(self):
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        address = map.get_houses_by_coordinates(lat, lon)
        address_str = ''
        if len(address):
            if address[0].get('address'):
                address = address[0].get('address')
                address_str = u'г. %s, ул. %s, д. %s' % (address.get('city'), address.get('street'), address.get('home'))
        logging.info(address)
        logging.info(address_str)
        self.render('/venues/edit_venue.html', **{
            'coordinates': '%s, %s' % (lat, lon) if lat else '',
            'address': address_str
        })

    def post(self):
        venue = Venue()
        raw_params = ('title', 'description', 'working_days', 'working_hours', 'holiday_schedule', 'problem')
        for param in raw_params:
            setattr(venue, param, self.request.get(param))
        venue.coordinates = ndb.GeoPt(self.request.get('coordinates'))
        venue.phone_numbers = [n.strip() for n in self.request.get('phone_numbers').split(',')]
        venue.put()
        self.redirect('/company/venues')


class EnableVenuesHandler(CompanyBaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        self.render('/venues/enable_venues.html', venues=venues)

    def post(self):
        venues = Venue.query().fetch()
        for v in venues:
            venue_id = str(v.key.id())
            new_active = bool(self.request.get(venue_id))
            if v.active != new_active:
                v.active = new_active
                v.put()
        self.render('/venues/enable_venues.html', venues=venues, success=True)


class EditVenueHandler(CompanyBaseHandler):
    def get(self, venue_id):
        venue = Venue.get_by_id(int(venue_id))
        if not venue:
            self.abort(404)
        self.render('/edit_venue.html', venue=venue)

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
        self.render('/venues/edit_venue.html', venue=venue, success=True)


class VenueListHandler(CompanyBaseHandler):
    def get(self):
        self.render('/menu/venue_list.html', **{
            'venues': Venue.query().fetch()
        })


class AddRestrictionHandler(CompanyBaseHandler):
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue_key = ndb.Key('Venue', venue_id)
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        categories = []
        for category in MenuCategory.query().fetch():
            products = []
            for product in category.menu_items:
                product = product.get()
                if product.status == STATUS_AVAILABLE:
                    if venue_key in product.restrictions:
                        product.avail = False
                    else:
                        product.avail = True
                    products.append(product)
            category.products = products
            categories.append(category)
        self.render('/menu/select_products_restriction.html', **{
            'categories': categories,
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


class MapVenuesHandler(CompanyBaseHandler):
    def get(self):
        venues = []
        for venue in Venue.query().fetch():
            venue.lat = venue.coordinates.lat
            venue.lon = venue.coordinates.lon
            venues.append(venue)
        self.render('/venues/map.html', **{
            'venues': venues
        })