import logging
from google.appengine.ext.ndb import GeoPt
from config import Config
from models import Venue
from requests import get_resto_venues
from company import get_company_schedule, get_delivery_types

__author__ = 'dvpermyakov'


def get_venues():
    config = Config.get()
    resto_company = config.RESTO_COMPANY.get()
    resto_venues = get_resto_venues(resto_company)
    venues = []
    logging.info('types = %s' % get_delivery_types())
    for resto_venue in resto_venues['venues']:
        venue = Venue(id=resto_venue['venueId'])
        venue.active = True
        venue.coordinates = GeoPt(lat=resto_venue['latitude'], lon=resto_venue['longitude'])
        venue.title = resto_venue['name']
        venue.description = resto_venue['address']
        venue.schedule = get_company_schedule()
        venue.delivery_types = get_delivery_types()
        venues.append(venue)
    return venues
