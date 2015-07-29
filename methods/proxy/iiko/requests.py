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


def get_iiko_venues(iiko_company):
    path = '/api/venues/%s' % iiko_company.resto_company_id
    return _get_request(path)


def get_iiko_payment_types(iiko_company):
    path = '/api/payment_types/%s' % iiko_company.key.id()
    return _get_request(path)