import logging

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES

__author__ = 'dvpermyakov'


MAX_VENUES = 20
MAX_RADIUS = 5
MIN_VENUES_IN_ONE_COMPANIES = 1


class ProxyCity(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    city = ndb.StringProperty(required=True)

    @classmethod
    def get_city_id(cls, city):
        for proxy_city in cls.query(cls.status == STATUS_AVAILABLE).fetch():
            if proxy_city.city == city:
                return proxy_city.key.id()

    def get_venues_by_company(self, company, location=None):
        from methods import location as location_methods
        from models import Venue
        init_namespace = namespace_manager.get_namespace()
        venues = []
        namespace_manager.set_namespace(company.namespace)
        for venue in Venue.query(Venue.active == True).fetch():
            if venue.address.city == self.city:
                venue.company_id = company.key.id
                venues.append(venue)
                if location:
                    venue.distance = location_methods.distance(location, venue.coordinates)
        if location:
            venues = sorted(venues, key=lambda venue: venue.distance)
        namespace_manager.set_namespace(init_namespace)
        return venues

    def get_venues(self, location=None):
        def _remove_venue(venue):
            for key, company_venues in companies_venues.iteritems():
                companies_venues[key] = company_venues.remove(venue)

        def _get_all_venues():
            venues = []
            for company_venues in companies_venues.values():
                venues.extend(company_venues)
            return venues

        companies_venues = {}
        for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch():
            companies_venues[company.key.id()] = self.get_venues_by_company(company, location)
        # case 1: remove all venues by radius
        while len(_get_all_venues()) > MAX_VENUES:
            for venue in sorted(_get_all_venues(), key=lambda venue: venue.distance):
                if venue.distance > MAX_RADIUS and len(companies_venues[venue.company_id]) > MIN_VENUES_IN_ONE_COMPANIES:
                    _remove_venue(venue)
            else:
                break
        # case 2: remove venues in overfull company
        while len(_get_all_venues()) > MAX_VENUES:
            overfull_company_venues = sorted(companies_venues,
                                             key=lambda company_venues: len(company_venues.values()))[0]
            _remove_venue(overfull_company_venues.values()[:-1])
        return _get_all_venues()

    def dict(self):
        return {
            'city': self.city,
            'id': str(self.key.id())
        }


class ProxyMenuItem(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    title = ndb.StringProperty(required=True)
    pic = ndb.StringProperty()

    def compare(self, item):
        return self.title in item.title

    def get_items(self, city, available_venues=None):
        from models import MenuItem
        init_namespace = namespace_manager.get_namespace()
        items = []
        for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch():
            venues = city.get_venues_by_company(company)
            namespace_manager.set_namespace(company.namespace)
            for item in MenuItem.query(MenuItem.status == STATUS_AVAILABLE).fetch():
                item.venues = []
                for venue in venues:
                    if venue.key in item.restrictions:
                        continue
                    if available_venues and venue not in available_venues:
                        continue
                    if self.compare(item):
                        item.venues.append(venue)
                        items.append(item)
        namespace_manager.set_namespace(init_namespace)
        return items

    def dict(self, min_price):
        return {
            'id': str(self.key.id()),
            'title': self.title,
            'pic': self.pic,
            'min_price': min_price
        }


class AutomationCompany(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    namespace = ndb.StringProperty(required=True)
    image = ndb.StringProperty()
    description = ndb.StringProperty()

    @classmethod
    def get_by_namespace(cls, namespace):
        for company in cls.query(cls.namespace == namespace).fetch():
            if company.namespace == namespace:
                return company

    def dict(self):
        from models.config.config import config, COMPANY_PREVIEW
        namespace_manager.set_namespace(self.namespace)
        return {
            'name': config.APP_NAME,
            'namespace': self.namespace,
            'image': self.image,
            'description': self.description,
            'preview': config.COMPANY_STATUS == COMPANY_PREVIEW,
        }
