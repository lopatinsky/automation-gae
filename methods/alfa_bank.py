import json
import logging
import urllib
from google.appengine.api import urlfetch
from config import config
from models import PaymentErrorsStatistics, AlfaBankRequest
from methods import email

ALPHA_CARD_LIMIT_CODES = [-20010, 902, 116, 123]
ALPHA_WRONG_CREDENTIALS_CODES = [71015]
CARD_LIMIT_CODE = 1
CARD_WRONG_CREDETIALS_CODE = 2

ACCEPTABLE_TOTAL_ERROR_PERCENTAGE = 0.2


def __post_request_alfa(api_path, params):

    error_statistics = PaymentErrorsStatistics.query().order(-PaymentErrorsStatistics.data_created).fetch(1)

    if not error_statistics:
        error_statistics = PaymentErrorsStatistics()
    else:
        error_statistics = error_statistics[0]

    logging.info(len(error_statistics.alfa_bank_requests))

    if len(error_statistics.alfa_bank_requests) >= 1000:
        error_statistics = PaymentErrorsStatistics()

    additional_error_statistics = None
    if len(error_statistics.alfa_bank_requests) < 100:
        additional_error_statistics = PaymentErrorsStatistics.query(
            PaymentErrorsStatistics.data_created < error_statistics.data_created).order(
                -PaymentErrorsStatistics.data_created).fetch(1)
    if additional_error_statistics:
        additional_error_statistics = additional_error_statistics[0]
    url = '%s%s' % (config.ALFA_BASE_URL, api_path)
    payload = json.dumps(params)
    logging.info(payload)
    if params:
        url = '%s?%s' % (url, urllib.urlencode(params))
    logging.info(url)
    content = urlfetch.fetch(url, method='POST', headers={'Content-Type': 'application/json'}, deadline=30,
                             validate_certificate=False).content

    result = json.loads(content)

    error_statistics.alfa_bank_requests.append(AlfaBankRequest(url=url, success=str(result.get('errorCode', '0')) == '0'))

    if len(error_statistics.alfa_bank_requests) <= 100:
        requests = error_statistics.alfa_bank_requests
    else:
        requests = error_statistics.alfa_bank_requests[len(error_statistics.alfa_bank_requests) - 100:]

    if additional_error_statistics:
        if len(additional_error_statistics.alfa_bank_requests) > (100 - len(requests)):
            requests.extend(additional_error_statistics.alfa_bank_requests[
                            len(additional_error_statistics.alfa_bank_requests) - (100 - len(requests)):])
        else:
            requests.extend(additional_error_statistics.alfa_bank_requests)

    check_error_statistics(requests)
    error_statistics.put()

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


def check_error_statistics(requests):
    error_number = sum(int(not request.success) for request in requests)
    if float(error_number) / len(requests) > ACCEPTABLE_TOTAL_ERROR_PERCENTAGE:
        email.send_error('server', 'payment errors', 'In the server there are a lot of suspicious errors')


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
