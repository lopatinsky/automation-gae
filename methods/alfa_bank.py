import json
import logging
import urllib
from google.appengine.api import urlfetch
from config import config
from models import PaymentErrorsStatistics
from datetime import datetime, timedelta
from methods import email

ALPHA_CARD_LIMIT_CODES = [-20010, 902, 116, 123]
ALPHA_WRONG_CREDENTIALS_CODES = [71015]
CARD_LIMIT_CODE = 1
CARD_WRONG_CREDETIALS_CODE = 2

ACCEPTABLE_SERIAL_ERROR_NUMBER = 3
MIN_TOTAL_REQUEST = 3
ACCEPTABLE_TOTAL_ERROR_PERCENTAGE = 0.5
PERIOD_HOUR = 1


def __post_request_alfa(api_path, params):

    time_hours_ago = datetime.now() - timedelta(hours=PERIOD_HOUR)
    statics_per_hours = PaymentErrorsStatistics.query(PaymentErrorsStatistics.data_created > time_hours_ago).fetch()
    if not statics_per_hours:
        statics_per_hours = PaymentErrorsStatistics()
    else:
        statics_per_hours = statics_per_hours[0]
    statics_per_hours.request_number += 1

    url = '%s%s' % (config.ALFA_BASE_URL, api_path)
    payload = json.dumps(params)
    logging.info(payload)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    content = urlfetch.fetch(url, method='POST', headers={'Content-Type': 'application/json'}, deadline=30,
                             validate_certificate=False).content

    result = json.loads(content)
    if str(result.get('errorCode', '0')) == '0':
        statics_per_hours.serial_error_number = 0
        if api_path == '/rest/registerPreAuth.do':
            statics_per_hours.registration_error_number = 0
        elif api_path == '/rest/reverse.do':
            statics_per_hours.reverse_error_number = 0
        elif api_path == '/rest/paymentOrderBinding.do':
            statics_per_hours.payment_error_number = 0
        elif api_path == '/rest/deposit.do':
            statics_per_hours.deposit_error_number = 0
        elif api_path == '/rest/unBindCard.do':
            statics_per_hours.unbind_error_number = 0
    else:
        statics_per_hours.total_error_number += 1
        statics_per_hours.serial_error_number += 1
        if api_path == '/rest/registerPreAuth.do':
            statics_per_hours.registration_error_number += 1
        elif api_path == '/rest/reverse.do':
            statics_per_hours.reverse_error_number += 1
        elif api_path == '/rest/paymentOrderBinding.do':
            statics_per_hours.payment_error_number += 1
        elif api_path == '/rest/deposit.do':
            statics_per_hours.deposit_error_number += 1
        elif api_path == '/rest/unBindCard.do':
            statics_per_hours.unbind_error_number += 1

    check_error_statistics(statics_per_hours)
    statics_per_hours.put()

    logging.info(content)
    return content


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
    elif result_json['actionCode'] in ALPHA_WRONG_CREDENTIALS_CODES:
        status_code = CARD_WRONG_CREDETIALS_CODE
    else:
        status_code = result_json['actionCode']
    return {'error_code': status_code,
            'description': result_json['actionCodeDescription'],
            'alfa_response': result_json}


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


def check_error_statistics(statistics):
    if statistics.registration_error_number > ACCEPTABLE_SERIAL_ERROR_NUMBER or \
            statistics.reverse_error_number > ACCEPTABLE_SERIAL_ERROR_NUMBER or \
            statistics.payment_error_number > ACCEPTABLE_SERIAL_ERROR_NUMBER or \
            statistics.deposit_error_number > ACCEPTABLE_SERIAL_ERROR_NUMBER or \
            statistics.unbind_error_number > ACCEPTABLE_SERIAL_ERROR_NUMBER or \
            statistics.serial_error_number > ACCEPTABLE_SERIAL_ERROR_NUMBER:
        email.send_error('alfa_bank', 'too_many_serial_errors',
                         'registration, reversion, payment, deposit, unbind or all together errors')

    if statistics.request_number > MIN_TOTAL_REQUEST and \
            statistics.total_error_number / statistics.request_number > ACCEPTABLE_TOTAL_ERROR_PERCENTAGE:
        email.send_error('alfa_bank', 'too_big_total_errors_percentage',
                         'total_errors_percentage: ' + str(statistics.total_error_number)
                         + ' > ' +
                         'acceptable percentage ' + str(ACCEPTABLE_TOTAL_ERROR_PERCENTAGE))


def hold_and_check(order_number, total_sum, return_url, client_id, binding_id):
    def success(resp):
        return str(resp.get('errorCode', '0')) == '0'

    tie_result = tie_card(total_sum * 100, order_number, return_url, client_id, 'MOBILE')
    if success(tie_result):
        payment_id = tie_result['orderId']
        create_result = create_pay(binding_id, payment_id)
        if success(create_result):
            check_result = check_extended_status(payment_id)['alfa_response']
            if success(check_result) and \
                    check_result['actionCode'] == 0 and check_result['orderStatus'] == 1:
                return payment_id
            else:
                logging.warning("extended status check fail")

    return None
