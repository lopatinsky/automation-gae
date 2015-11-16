from datetime import time
from google.appengine.ext.ndb import GeoPt
from methods.proxy.doubleb.requests import get_doubleb_venues
from models import Venue, STATUS_AVAILABLE
from models.proxy.doubleb import DoublebCompany
from models.schedule import Schedule, DaySchedule
from models.venue import DeliveryType, SELF, IN_CAFE

__author__ = 'dvpermyakov'


def _get_schedule(schedule_dicts):
    schedule = Schedule()
    for schedule_dict in schedule_dicts:
        start_hour = int(schedule_dict['hours'].split('-')[0]) % 24
        end_hour = int(schedule_dict['hours'].split('-')[1]) % 24
        for day in schedule_dict['days']:
            schedule.days.append(DaySchedule(weekday=int(day),
                                             start=time(hour=start_hour),
                                             end=time(hour=end_hour)))
    return schedule


def _get_delivery_types(takeout_only):
    delivery_types = []
    self_type = DeliveryType(delivery_type=SELF, status=STATUS_AVAILABLE)
    delivery_types.append(self_type)
    if not takeout_only:
        in_cafe_type = DeliveryType(delivery_type=IN_CAFE, status=STATUS_AVAILABLE)
        delivery_types.append(in_cafe_type)
    return delivery_types


def get_venues():
    company = DoublebCompany.get()
    venues_dict = get_doubleb_venues(company)['venues']
    venues = []
    for venue_dict in venues_dict:
        venue = Venue(id=int(venue_dict['id']))
        venue.active = True
        venue.coordinates = GeoPt(lat=venue_dict['coordinates'].split(',')[0],
                                  lon=venue_dict['coordinates'].split(',')[1])
        venue.title = venue_dict['title']
        venue.description = venue_dict['address']
        venue.schedule = _get_schedule(venue_dict['schedule'])
        venue.delivery_types = _get_delivery_types(venue_dict['takeout_only'])
        venue.update_timezone()
        venues.append(venue)
    return venues
