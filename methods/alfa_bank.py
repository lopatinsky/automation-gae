import json
import logging
import urllib
from google.appengine.api import urlfetch
from config import config
from models import PaymentErrorsStatistics

ALPHA_CARD_LIMIT_CODES = [-20010, 902, 116, 123]
ALPHA_WRONG_CREDENTIALS_CODES = [71015]
CARD_LIMIT_CODE = 1
CARD_WRONG_CREDETIALS_CODE = 2


def _error_code(resp):
    code = resp.get('errorCode')
    if code is None:
        code = resp.get('ErrorCode', '0')
    return int(code)


def _error_message(resp):
    return resp.get('errorMessage') or resp.get('ErrorMessage') or resp.get('error')


def _success(resp):
    return _error_code(resp) == 0


def __post_request_alfa(api_path, params, deadline=30):
    url = '%s%s' % (config.ALFA_BASE_URL, api_path)
    payload = json.dumps(params)
    logging.info(payload)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    content = urlfetch.fetch(url, method='POST', headers={'Content-Type': 'application/json'}, deadline=deadline,
                             validate_certificate=False).content
    logging.info(content)

    result = json.loads(content)
    code = _error_code(result)
    PaymentErrorsStatistics.append_request(
        url=api_path,
        success=code == 0,
        error_code=code,
        error_message=_error_message(result)
    )

    return result


def create(amount, order_number, return_url, client_id, page_view):
    p = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'amount': amount,
        'orderNumber': order_number,
        'returnUrl': return_url,
        'clientId': client_id,
        'pageView': page_view
    }
    result = __post_request_alfa('/rest/registerPreAuth.do', p, deadline=7)
    return result


def check_status(order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id
    }
    result = __post_request_alfa('/rest/getOrderStatus.do', params)
    return result


def check_extended_status(order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id,
    }
    result_json = __post_request_alfa('/rest/getOrderStatusExtended.do', params)
    if result_json['actionCode'] in ALPHA_CARD_LIMIT_CODES:
        status_code = CARD_LIMIT_CODE
    elif result_json['actionCode'] in ALPHA_WRONG_CREDENTIALS_CODES:
        status_code = CARD_WRONG_CREDETIALS_CODE
    else:
        status_code = result_json['actionCode']
    return {'error_code': status_code,
            'description': result_json['actionCodeDescription'],
            'alfa_response': result_json}


def reverse(order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id
    }
    result = __post_request_alfa('/rest/reverse.do', params)
    return result


def authorize(binding_id, order_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'mdOrder': order_id,
        'bindingId': binding_id
    }
    result = __post_request_alfa('/rest/paymentOrderBinding.do', params, deadline=40)
    return result


def deposit(order_id, amount):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'orderId': order_id,
        'amount': amount
    }
    result = __post_request_alfa('/rest/deposit.do', params)
    return result


def unbind_card(binding_id):
    params = {
        'userName': config.ALFA_LOGIN,
        'password': config.ALFA_PASSWORD,
        'bindingId': binding_id
    }
    result = __post_request_alfa('/rest/unBindCard.do', params)
    return result


def create_simple(amount, order_number, return_url, client_id):
    result = create(amount * 100, order_number, return_url, client_id, 'MOBILE')
    if not _success(result):
        return False, _error_message(result)
    return True, result['orderId']


def hold_and_check(payment_id, binding_id):
    create_result = authorize(binding_id, payment_id)
    if not _success(create_result):
        return False, _error_message(create_result)

    check_result = check_extended_status(payment_id)['alfa_response']
    if not _success(check_result):
        return False, _error_message(check_result)

    if not (check_result['actionCode'] == 0 and check_result['orderStatus'] == 1):
        logging.warning("extended status check fail")
        return False, check_result['actionCodeDescription']

    return True, payment_id
