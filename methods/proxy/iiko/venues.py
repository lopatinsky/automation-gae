from google.appengine.ext.ndb import GeoPt
from config import Config
from models import Venue
from models.schedule import Schedule
from requests import get_iiko_venues
from delivery_types import get_delivery_types

__author__ = 'dvpermyakov'


def get_venues():
    config = Config.get()
    iiko_company = config.IIKO_COMPANY.get()
    delivery_types = get_delivery_types()
    iiko_venues = get_iiko_venues(iiko_company)
    venues = []
    for iiko_venue in iiko_venues['venues']:
        venue = Venue()
        venue.faked_id = iiko_venue['venueId']
        venue.active = True
        venue.coordinates = GeoPt(lat=iiko_venue['latitude'], lon=iiko_venue['longitude'])
        venue.title = iiko_venue['name']
        venue.description = iiko_venue['address']
        venue.schedule = Schedule(days=[])
        venue.delivery_types = delivery_types
        venues.append(venue)
    return venues
