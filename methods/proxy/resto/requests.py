import json
import logging
import urllib
from google.appengine.api import urlfetch

__author__ = 'dvpermyakov'


BASE_URL = 'http://empatika-resto.appspot.com'


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
        payload = json.dumps(payload)
    logging.info('payload = %s' % payload)
    response = urlfetch.fetch(url, method='POST', payload=payload)
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



def get_resto_menu(resto_company):
    path = '/api/company/%s/menu' % resto_company.key.id()
    return _get_request(path)


def get_resto_company_info(resto_company):
    path = '/api/company/get_company'
    params = {
        'company_id': resto_company.key.id()
    }
    return _get_request(path, params)
