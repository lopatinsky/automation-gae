from handlers.api.base import ApiHandler
from models import PaymentType, STATUS_AVAILABLE

__author__ = 'ilyazorin'


class PaymentTypesHandler(ApiHandler):
    def get(self):
        payment_types = PaymentType.query(PaymentType.status == STATUS_AVAILABLE).fetch()
        self.render_json({
            'payment_types': [payment_type.dict() for payment_type in payment_types]
        })