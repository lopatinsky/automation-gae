# coding=utf-8
from base import ApiHandler
from config import config
from models import STATUS_AVAILABLE
from models.legal import LegalInfo

__author__ = 'dvpermyakov'


def _get_values(legal):
    return {
        'company_name': legal.name,
        'app_name': config.APP_NAME,
        'legal_person': legal.person_ooo if legal.person_ooo else legal.person_ip,
        'legal_person_ip': legal.person_ip,
        'site': legal.site,
        'legal_address': legal.address,
        'legal_inn': legal.inn,
        'legal_kpp': legal.kpp,
        'legal_ogrn': legal.ogrn,
        'legal_ogrnip': legal.ogrnip,
        'legal_contacts': legal.contacts,
        'legal_support_email': legal.email
    }


class AboutHandler(ApiHandler):
    def get(self):
        self.render_doc('about.html', **{
            'info': config.COMPANY_DESCRIPTION
        })


class LicenceHandler(ApiHandler):
    def get(self):
        for legal in LegalInfo.query(LegalInfo.status == STATUS_AVAILABLE).fetch():
            self.render_doc('auto_licence_agreement.html', **_get_values(legal))


class NdaHandler(ApiHandler):
    def get(self):
        self.render_doc('nda.html')


class PaymentRulesHandler(ApiHandler):
    def get(self):
        for legal in LegalInfo.query(LegalInfo.status == STATUS_AVAILABLE).fetch():
            self.render_doc('auto_payment_rules.html', **_get_values(legal))


class PaypalPrivacyPolicyHandler(ApiHandler):
    def get(self):
        for legal in LegalInfo.query(LegalInfo.status == STATUS_AVAILABLE).fetch():
            self.render_doc('auto_paypal_privacy_policy.html', **_get_values(legal))


class PaypalUserAgreementHandler(ApiHandler):
    def get(self):
        for legal in LegalInfo.query(LegalInfo.status == STATUS_AVAILABLE).fetch():
            self.render_doc('auto_paypal_user_agreement.html', **_get_values(legal))