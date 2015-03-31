from google.appengine.ext import ndb
from base import BaseHandler
from models import Venue, MenuItem


class VenueListHandler(BaseHandler):
    def get(self):
        self.render('menu/venue_list.html', **{
            'venues': Venue.query().fetch()
        })


class AddRestrictionHandler(BaseHandler):
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue_key = ndb.Key('Venue', str(venue_id))
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