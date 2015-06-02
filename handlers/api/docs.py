# coding=utf-8
from base import ApiHandler
from config import config

__author__ = 'dvpermyakov'


def _get_values():
    return {
        'company_name': config.COMPANY_NAME,
        'app_name': config.APP_NAME,
        'legal_person': config.LEGAL_PERSON,
        'site': config.SUPPORT_SITE,
        'legal_address': config.COMPANY_ADDRESS,
        'legal_inn': config.INN,
        'legal_kpp': config.KPP,
        'legal_ogrn': config.OGRN,
        'legal_contacts': config.LEGAL_CONTACTS,
        'legal_support_email': config.LEGAL_EMAIL
    }


class AboutHandler(ApiHandler):
    def get(self):
        self.render_doc('about.html', **{
            'info': config.COMPANY_DESCRIPTION
        })


class LicenceHandler(ApiHandler):
    def get(self):
        self.render_doc('auto_licence_agreement.html', **_get_values())


class NdaHandler(ApiHandler):
    def get(self):
        self.render_doc('nda.html')


class PaymentRulesHandler(ApiHandler):
    def get(self):
        self.render_doc('auto_payment_rules.html', **_get_values())