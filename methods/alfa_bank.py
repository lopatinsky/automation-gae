import json
import logging
import urllib
from google.appengine.api import urlfetch
from config import config

ALPHA_CARD_LIMIT_CODES = [-20010, 902, 116, 123]
CARD_LIMIT_CODE = 1

def __post_request_alfa(api_path, params):
    url = '%s%s' % (config.ALFA_BASE_URL, api_path)
    payload = json.dumps(params)
    logging.info(payload)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    return urlfetch.fetch(url, method='POST', headers={'Content-Type': 'application/json'}, deadline=30,
                          validate_certificate=False).content


def tie_card(amount, order_number, return_url, client_id, page_view):
    p = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'amount': amount,
        'orderNumber': order_number,
        'returnUrl': return_url,
        'clientId': client_id,
        'pageView': page_view
    }
    result = __post_request_alfa('/rest/registerPreAuth.do', p)
    return json.loads(result)


def check_status(order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id
    }
    result = __post_request_alfa('/rest/getOrderStatus.do', params)
    return json.loads(result)

def check_extended_status(order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id,
    }
    result = __post_request_alfa('/rest/getOrderStatusExtended.do', params)
    result_json = json.loads(result)
    if result_json['actionCode'] in ALPHA_CARD_LIMIT_CODES:
        status_code = CARD_LIMIT_CODE
    else:
        status_code = result_json['actionCode']
    return {'error_code': status_code,
            'description': result_json['actionCodeDescription']}

def get_back_blocked_sum(order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id
    }
    result = __post_request_alfa('/rest/reverse.do', params)
    return json.loads(result)


def create_pay(binding_id, order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'mdOrder': order_id,
        'bindingId': binding_id
    }
    result = __post_request_alfa('/rest/paymentOrderBinding.do', params)
    return json.loads(result)


def pay_by_card(order_id, amount):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id,
        'amount': amount
    }
    result = __post_request_alfa('/rest/deposit.do', params)
    return json.loads(result)


def unbind_card(binding_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'bindingId': binding_id
    }
    result = __post_request_alfa('/rest/unBindCard.do', params)
    return json.loads(result)
