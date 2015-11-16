import json
import logging
import urllib
from google.appengine.api import urlfetch
from methods.unique import get_temporary_user, USER_AGENT

BASE_URL = 'http://empatika-doubleb.appspot.com/'
BASE_URL_TEST = 'http://empatika-doubleb-test.appspot.com/'


def __get_base_url(company):
    if company.test_server:
        return BASE_URL_TEST
    else:
        return BASE_URL


def _get_request(company, path, params=None, log_response=True):
    url = '%s%s' % (__get_base_url(company), path)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    response = urlfetch.fetch(url, method='GET', deadline=60, headers={'User-Agent': get_temporary_user()[USER_AGENT]})
    logging.info(response.status_code)
    response = json.loads(response.content)
    if log_response:
        logging.info(response)
    return response


def _post_request(company, path, params=None, payload=None, log_response=True):
    url = '%s%s' % (__get_base_url(company), path)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    if payload:
        payload = {k: unicode(v).encode('utf-8') for k, v in payload.iteritems()}
        payload = urllib.urlencode(payload)
    logging.info('payload = %s' % payload)
    response = urlfetch.fetch(url, method='POST', payload=payload, deadline=60,
                              headers={'User-Agent': get_temporary_user()[USER_AGENT]})
    logging.info(response.status_code)
    response = json.loads(response.content)
    if log_response:
        logging.info(response)
    return response


def get_doubleb_venues(company):
    path = '/api/venues.php'
    return _get_request(company, path)


def get_doubleb_payment_types(company):
    path = '/api/payment/payment_types.php'
    return _get_request(company, path)
