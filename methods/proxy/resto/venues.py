from google.appengine.ext.ndb import GeoPt
from config import Config
from models import Venue
from requests import get_resto_venues
from delivery_types import get_delivery_types
from company import get_company_schedule

__author__ = 'dvpermyakov'


def get_venues():
    config = Config.get()
    resto_company = config.RESTO_COMPANY.get()
    delivery_types = get_delivery_types()
    resto_venues = get_resto_venues(resto_company)
    venues = []
    for resto_venue in resto_venues['venues']:
        venue = Venue(id=resto_venue['venueId'])
        venue.active = True
        venue.coordinates = GeoPt(lat=resto_venue['latitude'], lon=resto_venue['longitude'])
        venue.title = resto_venue['name']
        venue.description = resto_venue['address']
        venue.schedule = get_company_schedule()
        venue.delivery_types = delivery_types
        venues.append(venue)
    return venues
