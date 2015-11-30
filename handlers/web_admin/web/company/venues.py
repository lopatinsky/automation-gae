# coding:utf-8
from datetime import datetime
from google.appengine.ext import ndb
from base import CompanyBaseHandler
from methods.auth import venue_rights_required
from methods.rendering import STR_TIME_FORMAT
from models import Venue, MenuItem, MenuCategory, DeliveryZone
from methods import geocoder
from models.legal import LegalInfo
from models.schedule import DaySchedule, Schedule
from models.venue import DELIVERY


class CreateVenueHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        address = geocoder.get_houses_by_coordinates(lat, lon)
        address_str = ''
        if len(address):
            if address[0].get('address'):
                address = address[0].get('address')
                address_str = u'г. %s, ул. %s, д. %s' % (address.get('city'), address.get('street'), address.get('home'))
        if not address_str:
            self.redirect('/company/venues/map')
        else:
            legals = LegalInfo.query().fetch()
            self.render('/venues/edit_venue.html', **{
                'DEFAULT_EMAIL': 'elenamarchenko.lm@gmail.com',
                'legals': legals,
                'lat': lat,
                'lon': lon,
                'address': address_str
            })

    @venue_rights_required
    def post(self):
        venue = Venue()
        venue.title = self.request.get('title')
        venue.description = self.request.get('description')
        venue.phones = self.request.get('phones').split(',')
        venue.emails = self.request.get('emails').split(',')
        venue.coordinates = ndb.GeoPt(float(self.request.get('lat')), float(self.request.get('lon')))
        venue.legal = LegalInfo.get_by_id(self.request.get_range('legal')).key
        venue.update_address()
        venue.put()
        self.redirect('/company/venues')


class EnableVenuesHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        venues = Venue.query().fetch()
        for venue in venues:
            venue.days = [day for day in venue.schedule.days] if venue.schedule else []
        self.render('/venues/enable_venues.html', venues=venues)

    @venue_rights_required
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
    @venue_rights_required
    def get(self, venue_id):
        venue = Venue.get_by_id(int(venue_id))
        if not venue:
            self.abort(404)
        legals = LegalInfo.query().fetch()
        self.render('/venues/edit_venue.html', venue=venue, legals=legals)

    @venue_rights_required
    def post(self, venue_id):
        venue = Venue.get_by_id(int(venue_id))
        if not venue:
            self.abort(404)
        venue.title = self.request.get('title')
        venue.description = self.request.get('description')
        venue.phones = self.request.get('phones').split(',')
        venue.emails = self.request.get('emails').split(',')
        venue.legal = LegalInfo.get_by_id(int(self.request.get('legal'))).key
        venue.put()
        legals = LegalInfo.query().fetch()
        self.render('/venues/edit_venue.html', venue=venue, success=True, legals=legals)


class VenueListHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        self.render('/menu/venue_list.html', **{
            'venues': Venue.query().fetch()
        })


class AddRestrictionHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue_key = ndb.Key('Venue', venue_id)
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        categories = []
        for category in MenuCategory.query().fetch():
            products = []
            for product in category.get_items(only_available=True):
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

    @venue_rights_required
    def post(self):
        venue_id = self.request.get_range('venue_id')
        venue_key = ndb.Key('Venue', venue_id)
        for product in MenuItem.query().fetch():
            confirmed_product = bool(self.request.get(str(product.key.id())))
            if product.category and self.request.get(str(product.category.id())):
                confirmed_product = True
            if venue_key in product.restrictions:
                if confirmed_product:
                    product.restrictions.remove(venue_key)
                    product.put()
            else:
                if not confirmed_product:
                    product.restrictions.append(venue_key)
                    product.put()
        self.redirect_to('venues_list')


class MapVenuesHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        venues = []
        for venue in Venue.query().fetch():
            venue.lat = venue.coordinates.lat
            venue.lon = venue.coordinates.lon
            venues.append(venue)
        self.render('/venues/map.html', **{
            'venues': venues
        })


class ChooseDeliveryZonesHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        venue_zone_keys = []
        for delivery in venue.delivery_types:
            if delivery.delivery_type == DELIVERY:
                venue_zone_keys = delivery.delivery_zones
        zones = DeliveryZone.query().order(DeliveryZone.sequence_number).fetch()
        for zone in zones:
            zone.address_str = zone.address.str()
            if zone.key in venue_zone_keys:
                zone.has = True
            else:
                zone.has = False
        self.render('/venues/choose_zones.html', zones=zones, venue=venue)

    @venue_rights_required
    def post(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        found_delivery = None
        for delivery in venue.delivery_types:
            if delivery.delivery_type == DELIVERY:
                found_delivery = delivery
        if not found_delivery:
            self.abort(400)
        zones = DeliveryZone.query().fetch()
        for zone in zones:
            confirmed = bool(self.request.get(str(zone.key.id())))
            if confirmed:
                if zone.key not in found_delivery.delivery_zones:
                    found_delivery.delivery_zones.append(zone.key)
            else:
                if zone.key in found_delivery.delivery_zones:
                    found_delivery.delivery_zones.remove(zone.key)
        venue.put()
        self.redirect('/company/venues')


class EditVenueScheduleHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        days = []
        venue_days = {}
        if venue.schedule:
            for day in venue.schedule.days:
                venue_days[day.weekday] = {
                    'start': day.start_str(),
                    'end': day.end_str()
                }
        for day in DaySchedule.DAYS:
            days.append({
                'name': DaySchedule.DAY_MAP[day],
                'value': day,
                'exist': True if venue_days.get(day) else False,
                'start': venue_days[day]['start'] if venue_days.get(day) else '00:00',
                'end': venue_days[day]['end'] if venue_days.get(day) else '00:00'
            })
        self.render('/schedule.html', **{
            'venue': venue,
            'days': days
        })

    @venue_rights_required
    def post(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        days = []
        for day in DaySchedule.DAYS:
            confirmed = bool(self.request.get(str(day)))
            if confirmed:
                start = datetime.strptime(self.request.get('start_%s' % day), STR_TIME_FORMAT)
                end = datetime.strptime(self.request.get('end_%s' % day), STR_TIME_FORMAT)
                days.append(DaySchedule(weekday=day, start=start.time(), end=end.time()))
        schedule = Schedule(days=days)
        venue.schedule = schedule
        venue.put()
        self.redirect('/company/venues')


class EditVenueTimeBreakHandler(CompanyBaseHandler):
    @venue_rights_required
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        index = self.request.get_range('index')
        days = []
        venue_days = {}
        if len(venue.time_break) > index and venue.time_break[index]:
            for day in venue.time_break[index].days:
                venue_days[day.weekday] = {
                    'start': day.start_str(),
                    'end': day.end_str()
                }
        for day in DaySchedule.DAYS:
            days.append({
                'name': DaySchedule.DAY_MAP[day],
                'value': day,
                'exist': True if venue_days.get(day) else False,
                'start': venue_days[day]['start'] if venue_days.get(day) else '00:00',
                'end': venue_days[day]['end'] if venue_days.get(day) else '00:00'
            })
        self.render('/schedule.html', **{
            'venue': venue,
            'days': days,
            'index': index
        })

    @venue_rights_required
    def post(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        index = self.request.get_range('index')
        days = []
        for day in DaySchedule.DAYS:
            confirmed = bool(self.request.get(str(day)))
            if confirmed:
                start = datetime.strptime(self.request.get('start_%s' % day), STR_TIME_FORMAT)
                end = datetime.strptime(self.request.get('end_%s' % day), STR_TIME_FORMAT)
                days.append(DaySchedule(weekday=day, start=start.time(), end=end.time()))
        schedule = Schedule(days=days)
        if not venue.time_break:
            venue.time_break = [schedule]
        elif len(venue.time_break) > index:
            venue.time_break[index] = schedule
        else:
            venue.time_break.append(schedule)
        venue.put()
        self.redirect('/company/venues')
