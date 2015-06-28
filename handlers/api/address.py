import json
import logging
from base import ApiHandler
from methods.address_validation import check_address
from methods.map import get_houses_by_address, get_streets_or_houses_by_address
from methods.orders.validation.precheck import validate_address

__author__ = 'dvpermyakov'


class AddressByAddressHandler(ApiHandler):
    def get(self):
        city = self.request.get('city')
        street = self.request.get('street').capitalize()
        if ',' in street:
            home = street.split(',')[1]
            street = street.split(',')[0]
            response = get_houses_by_address(city, street, home)
        else:
            response = get_streets_or_houses_by_address(city, street)
        logging.info('response = %s' % response)
        self.render_json(response)


class ValidateAddressHandler(ApiHandler):
    def get(self):
        address = self.request.get('address')
        if not address:
            self.abort(400)
        address = json.loads(address)
        address = validate_address(address)
        success, description = check_address(address)
        self.render_json({
            'success': success,
            'description': description
        })
