# coding=utf-8
from google.appengine.api.namespace_manager import namespace_manager

from methods.cities import get_company_cities
from methods.rendering import get_location
from models import STATUS_AVAILABLE
from models.proxy.unified_app import AutomationCompany, ProxyMenuItem
from ..base import ApiHandler


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
        self.render_json({
            'cities': get_company_cities()
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
        items = ProxyMenuItem.query().fetch()
        result = []
        for item in items:
            real_items = item.get_items(self.request.city)
            if not real_items:
                continue
            min_price = min(i.price for i in real_items) / 100.0
            result.append(item.dict(min_price))
        self.render_json({
            'items': result
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
