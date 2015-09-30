import logging

from .base import ApiHandler
from models.config.config import config
from methods import alfa_bank
from models import CardBindingPayment, Client


class UnbindCardHandler(ApiHandler):
    def post(self):
        binding_id = self.request.get("bindingId")

        alfa_response = alfa_bank.unbind_card(config.ALFA_LOGIN, config.ALFA_PASSWORD, binding_id)
        self.render_json(alfa_response)


class PaymentRegisterHandler(ApiHandler):
    def post(self):
        client_id = self.request.get("clientId")
        order_number = self.request.get("orderNumber")
        amount = self.request.get("amount")
        return_url = self.request.get("returnUrl")

        alfa_response = alfa_bank.create(config.ALFA_LOGIN, config.ALFA_PASSWORD, amount, order_number, return_url,
                                         client_id, 'MOBILE')
        if str(alfa_response.get('errorCode', '0')) == '0':
            CardBindingPayment(id=alfa_response['orderId'], client_id=int(client_id)).put()
        self.render_json(alfa_response)


class PaymentReverseHandler(ApiHandler):
    def post(self):
        order_id = self.request.get('orderId') or self.request.get('order_id')

        alfa_response = alfa_bank.reverse(config.ALFA_LOGIN, config.ALFA_PASSWORD, order_id)
        self.render_json(alfa_response)


class PaymentStatusHandler(ApiHandler):
    def post(self):
        order_id = self.request.get('orderId')

        result = alfa_bank.check_extended_status(config.ALFA_LOGIN, config.ALFA_PASSWORD, order_id)['alfa_response']
        alfa_response = {}

        if 'errorCode' in result:
            alfa_response['ErrorCode'] = result['errorCode']
            alfa_response['errorCode'] = result['errorCode']
            if alfa_response['ErrorCode'] == '0':
                if result.get('actionCode') != 0:
                    alfa_response['ErrorCode'] = '1'
                    alfa_response['errorCode'] = '1'

        if 'orderStatus' in result:
            alfa_response['OrderStatus'] = result['orderStatus']
            alfa_response['orderStatus'] = result['orderStatus']

        if result.get('cardAuthInfo'):
            if result['cardAuthInfo'].get('pan'):
                alfa_response['Pan'] = result['cardAuthInfo']['pan']
                alfa_response['pan'] = result['cardAuthInfo']['pan']
            if result['cardAuthInfo'].get('expiration'):
                alfa_response['expiration'] = result['cardAuthInfo']['expiration']

        if 'orderNumber' in result:
            alfa_response['OrderNumber'] = result['orderNumber']
            alfa_response['orderNumber'] = result['orderNumber']

        alfa_response['bindingId'] = None
        if result.get('bindingInfo'):
            if result['bindingInfo'].get('bindingId'):
                alfa_response['bindingId'] = result['bindingInfo']['bindingId']

        binding = CardBindingPayment.get_by_id(order_id)
        if alfa_response['OrderStatus'] == 1:
            binding.success = True
            client = Client.get_by_id(binding.client_id)
            client.tied_card = True
            client.put()
        else:
            binding.success = False
            binding.error = result.get('actionCode')
            binding.error_description = result.get('actionCodeDescription')
        binding.put()

        self.render_json(alfa_response)


class PaymentExtendedStatusHandler(ApiHandler):
    def post(self):
        order_id = self.request.get('orderId')

        alfa_response = alfa_bank.check_extended_status(config.ALFA_LOGIN, config.ALFA_PASSWORD, order_id)
        logging.info(alfa_response)

        self.render_json(alfa_response)
