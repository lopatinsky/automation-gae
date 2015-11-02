from google.appengine.api import memcache
from google.appengine.ext.ndb import GeoPt
from models import Venue
from models.proxy.resto import RestoCompany
from requests import get_resto_venues
from company import get_company_schedule, get_delivery_types

__author__ = 'dvpermyakov'


def get_venues():
    resto_company = RestoCompany.get()
    venues = memcache.get('venues_%s' % resto_company.key.id())
    if not venues:
        resto_venues = get_resto_venues(resto_company)
        venues = []
        for resto_venue in resto_venues['venues']:
            venue = Venue(id=resto_venue['venueId'])
            venue.active = True
            venue.coordinates = GeoPt(lat=resto_venue['latitude'], lon=resto_venue['longitude'])
            venue.title = resto_venue['name']
            venue.description = resto_venue['address']
            venue.schedule = get_company_schedule()
            venue.delivery_types = get_delivery_types()
            venue.update_timezone()
            venues.append(venue)
        memcache.set('venues_%s' % resto_company.key.id(), venues, time=3600)
    return venues
