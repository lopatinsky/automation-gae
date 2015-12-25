import base64

from models import STATUS_AVAILABLE
from models.menu import MenuItem
from models.proxy.unified_app import AutomationCompany, ProxyCity
from models.venue import Venue


def get_company_cities():
    companies = AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch()
    if companies:
        return [city.dict() for city in ProxyCity.query(ProxyCity.status == STATUS_AVAILABLE).fetch()]
    else:
        found = False
        for venue in Venue.query(Venue.active == True).fetch():
            if MenuItem.query(MenuItem.restrictions.IN((venue.key,))).get():
                found = True
        if not found:
            return []
        cities = Venue.get_cities()
        if len(cities) > 1:
            return [{
                'city': city,
                'id': base64.b64encode(city.encode('utf-8'))
            } for city in cities]
        else:
            return []
