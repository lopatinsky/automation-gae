import json
import logging
import urllib
from google.appengine.api import urlfetch
from methods.rendering import timestamp

__author__ = 'dvpermyakov'


BASE_URL = 'http://empatika-resto-test.appspot.com'


def _get_request(path, params=None, log_response=True):
    url = '%s%s' % (BASE_URL, path)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    response = urlfetch.fetch(url, method='GET')
    logging.info(response.status_code)
    response = json.loads(response.content)
    if log_response:
        logging.info(response)
    return response


def _post_request(path, params=None, payload=None, log_response=True):
    url = '%s%s' % (BASE_URL, path)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    if payload:
        payload = {k: unicode(v).encode('utf-8') for k, v in payload.iteritems()}
        payload = urllib.urlencode(payload)
    logging.info('payload = %s' % payload)
    response = urlfetch.fetch(url, method='POST', payload=payload, deadline=60)
    logging.info(response.status_code)
    response = json.loads(response.content)
    if log_response:
        logging.info(response)
    return response


def get_resto_venues(resto_company):
    path = '/api/venues/%s' % resto_company.key.id()
    return _get_request(path)


def get_resto_payment_types(resto_company):
    path = '/api/company/%s/payment_types' % resto_company.key.id()
    return _get_request(path)


def get_resto_delivery_types(resto_company):
    path = '/api/delivery_types'
    params = {
        'organization_id': resto_company.key.id()
    }
    return _get_request(path, params)


def get_resto_menu(resto_company):
    path = '/api/company/%s/menu' % resto_company.key.id()
    return _get_request(path, log_response=False)


def get_resto_company_info(resto_company):
    path = '/api/company/get_company'
    params = {
        'company_id': resto_company.key.id()
    }
    return _get_request(path, params)


def get_resto_promos(resto_company):
    path = '/api/company/%s/promos' % resto_company.key.id()
    return _get_request(path)


def post_resto_register(resto_company, resto_customer):
    path = '/api/customer/register'
    payload = {
        'company_id': resto_company.key.id(),
        'customer_id': resto_customer.resto_customer_id if resto_customer else None
    }
    return _post_request(path, payload=payload)


def post_resto_check_order(venue, resto_item_dicts, auto_client, resto_client, total_sum, delivery_time):
    path = '/api/get_order_promo'
    payload = {
        'venue_id': venue.key.id(),
        'phone': auto_client.tel,
        'customer_id': resto_client.key.id() if resto_client else None,
        'sum': total_sum,
        'date': timestamp(delivery_time),
        'items': json.dumps(resto_item_dicts)
    }
    return _post_request(path, payload=payload)


def post_resto_place_order(resto_venue, resto_customer, auto_client, order, items, payment_dict, address):
    from methods.proxy.resto.company import REVERSE_DELIVERY_TYPE_MAP
    from methods.proxy.resto.payment_types import REVERSE_PAYMENT_TYPE_MAP
    path = '/api/venue/%s/order/new' % resto_venue.key.id()
    payload = {
        'custom_data': '',
        'bonus_sum': 0,
        'discount_sum': 0,
        'customer_id': resto_customer.resto_customer_id,
        'address': json.dumps(address),
        'comment': order.comment,
        'binding_id': payment_dict.get('binding_id'),
        'alpha_client_id': payment_dict.get('client_id'),
        'name': auto_client.name,
        'phone': auto_client.tel,
        'date': timestamp(order.delivery_time),
        'paymentType': REVERSE_PAYMENT_TYPE_MAP[order.payment_type_id],
        'items': json.dumps(items),
        'sum': order.total_sum,
        'deliveryType': REVERSE_DELIVERY_TYPE_MAP[order.delivery_type]
    }
    return _post_request(path, payload=payload)

