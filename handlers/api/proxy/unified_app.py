# coding=utf-8
from google.appengine.api.namespace_manager import namespace_manager
from ..base import ApiHandler
from methods.rendering import get_location
from models import STATUS_AVAILABLE, MenuItem, Venue
from models.proxy.unified_app import AutomationCompany, ProxyCity, ProxyMenuItem
import base64


class CompaniesHandler(ApiHandler):
    def get(self):
        if self.request.init_namespace:
            namespace_manager.set_namespace(self.request.init_namespace)
        self.render_json({
            'companies': [company.dict()
                          for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch()]
        })


class CitiesHandler(ApiHandler):
    def get(self):
        companies = AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch()
        if companies:
            cities_dict = [city.dict() for city in ProxyCity.query(ProxyCity.status == STATUS_AVAILABLE).fetch()]
        else:
            found = False
            for venue in Venue.query(Venue.active == True).fetch():
                if MenuItem.query(MenuItem.restrictions.IN((venue.key,))).get():
                    found = True
            if not found:
                return self.render_json({})
            cities = Venue.get_cities()
            if len(cities) > 1:
                cities_dict = [{
                    'city': city,
                    'id': city
                } for city in cities]
            else:
                return self.render_json({})
        self.render_json({
            'cities': cities_dict
        })


class VenuesHandler(ApiHandler):
    def get(self):
        if not self.request.city:
            self.abort(400)
        location = get_location(self.request.get("ll"))
        self.render_json({
            'venues': [venue.dict(user_location=location) for venue in self.request.city.get_venues(location)]
        })


class MenuHandler(ApiHandler):
    def get(self):
        if not self.request.city:
            self.abort(400)
        self.render_json({
            'items': [item.dict() for item in ProxyMenuItem.query(ProxyMenuItem.status == STATUS_AVAILABLE).fetch()
                      if item.get_items(self.request.city)]
        })


class ProductHandler(ApiHandler):
    def get(self):
        if not self.request.city:
            self.abort(400)
        product_id = self.request.get_range('product_id')
        product = ProxyMenuItem.get_by_id(product_id)
        if not product:
            self.abort(400)
        location = get_location(self.request.get("ll"))
        available_venues = self.request.city.get_venues(location)
        venues_dict = {}
        init_namespace = namespace_manager.get_namespace()
        for item in product.get_items(self.request.city, available_venues):
            for venue in item.venues:
                namespace_manager.set_namespace(init_namespace)
                company = AutomationCompany.get_by_namespace(item.key.namespace())
                namespace_manager.set_namespace(item.key.namespace())
                dct = venues_dict.get(venue.key.id())
                if not dct:
                    dct = {
                        'venue_info': venue.dict(),
                        'company': company.dict(),
                        'items': []
                    }
                    venues_dict[venue.key.id()] = dct
                dct['items'].append(item.dict())
        self.render_json({
            'venues': venues_dict.values()
        })
