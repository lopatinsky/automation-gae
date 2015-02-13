import logging
from .base import ApiHandler
from methods import alfa_bank
from models import CardBindingPayment, Client


class UnbindCardHandler(ApiHandler):
    def post(self):
        binding_id = self.request.get("bindingId")

        alfa_response = alfa_bank.unbind_card(binding_id)
        self.render_json(alfa_response)


class PaymentBindingHandler(ApiHandler):
    def post(self):
        binding_id = self.request.get("bindingId")
        order_id = self.request.get("mdOrder")

        alfa_response = alfa_bank.authorize(binding_id, order_id)
        self.render_json(alfa_response)


class PaymentRegisterHandler(ApiHandler):
    def post(self):
        client_id = self.request.get("clientId")
        order_number = self.request.get("orderNumber")
        amount = self.request.get("amount")
        return_url = self.request.get("returnUrl")

        alfa_response = alfa_bank.create(amount, order_number, return_url, client_id, 'MOBILE')
        if str(alfa_response.get('errorCode', '0')) == '0':
            CardBindingPayment(id=alfa_response['orderId'], client_id=int(client_id)).put()
        self.render_json(alfa_response)


class PaymentReverseHandler(ApiHandler):
    def post(self):
        order_id = self.request.get('orderId') or self.request.get('order_id')

        alfa_response = alfa_bank.reverse(order_id)
        self.render_json(alfa_response)


class PaymentStatusHandler(ApiHandler):
    def post(self):
        order_id = self.request.get('orderId')

        result = alfa_bank.check_extended_status(order_id)
        alfa_response = result['alfa_response']

        if 'errorCode' in alfa_response:
            alfa_response['ErrorCode'] = alfa_response['errorCode']
            if alfa_response['ErrorCode'] == 0:
                if alfa_response['actionCode'] != 0:
                    alfa_response['ErrorCode'] = 1

        if 'orderStatus' in alfa_response:
            alfa_response['OrderStatus'] = alfa_response['orderStatus']

        if alfa_response.get('cardAuthInfo'):
            if alfa_response['cardAuthInfo'].get('pan'):
                alfa_response['Pan'] = alfa_response['cardAuthInfo']['pan']
            if alfa_response['cardAuthInfo'].get('expiration'):
                alfa_response['expiration'] = alfa_response['cardAuthInfo']['expiration']

        if 'orderNumber' in alfa_response:
            alfa_response['OrderNumber'] = alfa_response['orderNumber']

        alfa_response['bindingId'] = None
        if alfa_response.get('bindingInfo'):
            if alfa_response['bindingInfo'].get('bindingId'):
                alfa_response['bindingId'] = alfa_response['bindingInfo']['bindingId']

        binding = CardBindingPayment.get_by_id(order_id)
        if alfa_response['OrderStatus'] == 1:
            binding.success = True
            client = Client.get_by_id(binding.client_id)
            client.tied_card = True
            client.put()
        else:
            binding.success = False
            binding.error = alfa_response.get('actionCode')
            binding.error_description = alfa_response.get('actionCodeDescription')
        binding.put()

        self.render_json(alfa_response)


class PaymentExtendedStatusHandler(ApiHandler):
    def post(self):
        order_id = self.request.get('orderId')

        alfa_response = alfa_bank.check_extended_status(order_id)
        logging.info(alfa_response)

        self.render_json(alfa_response)
