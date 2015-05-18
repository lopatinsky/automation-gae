from base import ApiHandler
from methods.map import get_houses_by_address, get_streets_or_houses_by_address

__author__ = 'dvpermyakov'


class AddressByAddressHandler(ApiHandler):
    def get(self):
        city = self.request.get('city')
        street = self.request.get('street')
        if ',' in street:
            home = street.split(',')[0]
            street = street.split(',')[1]
            return self.render_json(get_houses_by_address(city, street, home))
        else:
            return self.render_json(get_streets_or_houses_by_address(city, street))