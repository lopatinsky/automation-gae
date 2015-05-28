# coding=utf-8
from base import ApiHandler
from config import config

__author__ = 'dvpermyakov'


def _get_values():
    return {
        'company_name': 'Meat Me Co',
        'app_name': 'Meat Me',
        'legal_person': u'ИП Иванов Иван Иванович',
        'site': 'www.site.ru',
        'legal_address': u'ул. Пушкина, дом. Колотушкина',
        'legal_inn': 1241241241,
        'legal_kpp': 412412412,
        'legal_ogrn': 14124124124,
        'legal_contacts': '+79152965155',
        'legal_support_email': 'dvpermyakov1@gmail.com'
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