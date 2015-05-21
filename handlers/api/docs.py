from base import ApiHandler
from config import config

__author__ = 'dvpermyakov'


class AboutHandler(ApiHandler):
    def get(self):
        self.render_doc('about.html', **{
            'info': config.COMPANY_DESCRIPTION
        })


class LicenceHandler(ApiHandler):
    def get(self):
        self.render_doc('licence_agreement.html')


class NdaHandler(ApiHandler):
    def get(self):
        self.render_doc('licence_agreement.html')


class PaymentRulesHandler(ApiHandler):
    def get(self):
        self.render_doc('payment_rules.html')