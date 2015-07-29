from google.appengine.ext.ndb import GeoPt
from config import Config
from models import Venue, STATUS_AVAILABLE
from models.schedule import Schedule
from models.venue import DeliveryType, DELIVERY
from requests import get_iiko_venues

__author__ = 'dvpermyakov'


def get_venues():
    config = Config.get()
    iiko_company = config.IIKO_COMPANY.get()
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
        venue.delivery_types = [DeliveryType(delivery_type=DELIVERY, status=STATUS_AVAILABLE)]
        venues.append(venue)
    return venues
