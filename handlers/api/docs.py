# coding=utf-8
from google.appengine.api import namespace_manager
from jinja2 import TemplateNotFound
from base import ApiHandler
from models.config.config import config
from models import STATUS_AVAILABLE
from models.legal import LegalInfo
from models.payment_types import PaymentType, CARD_PAYMENT_TYPE

__author__ = 'dvpermyakov'


def _get_values(legal):
    return {
        'company_name': legal.name,
        'app_name': u"«%s»" % config.APP_NAME,
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
        cards_enabled = False
        cpt = PaymentType.get(CARD_PAYMENT_TYPE)
        if cpt and cpt.status == STATUS_AVAILABLE:
            cards_enabled = True

        info = config.get_company_dict()
        self.render_doc('about.html', **{
            'info': info['description'],
            'phone': info['phone'],
            'cards_enabled': cards_enabled,
        })


class LicenceHandler(ApiHandler):
    def get(self):
        try:
            self.render_doc('%s/licence_agreement.html' % namespace_manager.get_namespace())
        except TemplateNotFound:
            for legal in LegalInfo.query(LegalInfo.status == STATUS_AVAILABLE).fetch():
                self.render_doc('auto_licence_agreement.html', **_get_values(legal))


class NdaHandler(ApiHandler):
    def get(self):
        self.render_doc('nda.html')


class PaymentRulesHandler(ApiHandler):
    def get(self):
        try:
            self.render_doc('%s/payment_rules.html' % namespace_manager.get_namespace())
        except TemplateNotFound:
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