from methods.auth import payment_types_rights_required
from models import PaymentType, STATUS_UNAVAILABLE, STATUS_AVAILABLE
from base import CompanyBaseHandler
from models.payment_types import CASH_PAYMENT_TYPE, CARD_PAYMENT_TYPE, PAYPAL_PAYMENT_TYPE, CARD_COURIER_PAYMENT_TYPE

__author__ = 'dvpermyakov'


class PaymentTypesHandler(CompanyBaseHandler):
    @payment_types_rights_required
    def get(self):
        cash = PaymentType.get_by_id(str(CASH_PAYMENT_TYPE))
        if not cash:
            PaymentType(id=str(CASH_PAYMENT_TYPE), title='cash', status=STATUS_UNAVAILABLE).put()
        card = PaymentType.get_by_id(str(CARD_PAYMENT_TYPE))
        if not card:
            PaymentType(id=str(CARD_PAYMENT_TYPE), title='card', status=STATUS_UNAVAILABLE).put()
        paypal = PaymentType.get_by_id(str(PAYPAL_PAYMENT_TYPE))
        if not paypal:
            PaymentType(id=str(PAYPAL_PAYMENT_TYPE), title='paypal', status=STATUS_UNAVAILABLE).put()
        courier_card = PaymentType.get_by_id(str(CARD_COURIER_PAYMENT_TYPE))
        if not courier_card:
            PaymentType(id=str(CARD_COURIER_PAYMENT_TYPE), title='courier card', status=STATUS_UNAVAILABLE).put()
        self.render('/payment_types.html', payments=PaymentType.query().fetch(),
                    CARD_PAYMENT_TYPE=str(CARD_PAYMENT_TYPE))

    @payment_types_rights_required
    def post(self):
        for payment in PaymentType.query().fetch():
            confirmed = bool(self.request.get(str(payment.key.id())))
            if bool(payment.status) != confirmed:
                if confirmed:
                    payment.status = STATUS_AVAILABLE
                else:
                    payment.status = STATUS_UNAVAILABLE
                payment.put()
        self.redirect('/company/main')
