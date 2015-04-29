from methods.auth import company_user_required
from models import PaymentType, CASH_PAYMENT_TYPE, STATUS_UNAVAILABLE, CARD_PAYMENT_TYPE, WALLET_PAYMENT_TYPE, STATUS_AVAILABLE
from base import CompanyBaseHandler


__author__ = 'dvpermyakov'


class PaymentTypesHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        cash = PaymentType.get_by_id(str(CASH_PAYMENT_TYPE))
        if not cash:
            PaymentType(id=str(CASH_PAYMENT_TYPE), title='cash', status=STATUS_UNAVAILABLE).put()
        card = PaymentType.get_by_id(str(CARD_PAYMENT_TYPE))
        if not card:
            PaymentType(id=str(CARD_PAYMENT_TYPE), title='card', status=STATUS_UNAVAILABLE).put()
        wallet = PaymentType.get_by_id(str(WALLET_PAYMENT_TYPE))
        if not wallet:
            PaymentType(id=str(WALLET_PAYMENT_TYPE), title='wallet', status=STATUS_UNAVAILABLE).put()
        self.render('/payment_types.html', payments=PaymentType.query().fetch())

    @company_user_required
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