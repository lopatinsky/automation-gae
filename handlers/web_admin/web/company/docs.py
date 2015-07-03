from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from base import CompanyBaseHandler
from methods.auth import company_user_required
from config import config, Config
from models.legal import LegalInfo

__author__ = 'dvpermyakov'


def _get_values():
    return {
        'name': config.APP_NAME if config.APP_NAME else '',
        'info': config.COMPANY_DESCRIPTION if config.COMPANY_DESCRIPTION else '',
        'company_name': config.COMPANY_NAME if config.COMPANY_NAME else '',
        'company_address': config.COMPANY_ADDRESS if config.COMPANY_ADDRESS else '',
        'phone': config.SUPPORT_PHONE if config.SUPPORT_PHONE else '',
        'site': config.SUPPORT_SITE if config.SUPPORT_SITE else '',
        'emails': u','.join(config.SUPPORT_EMAILS),
        'delivery_phones': u','.join(config.DELIVERY_PHONES),
        'delivery_emails':  u','.join(config.DELIVERY_EMAILS),
        'legal_person': config.LEGAL_PERSON if config.LEGAL_PERSON else '',
        'legal_person_ip': config.LEGAL_PERSON_IP if config.LEGAL_PERSON_IP else '',
        'legal_contacts': config.LEGAL_CONTACTS if config.LEGAL_CONTACTS else '',
        'legal_email': config.LEGAL_EMAIL if config.LEGAL_EMAIL else '',
        'inn': config.INN if config.INN else '',
        'kpp': config.KPP if config.KPP else '',
        'ogrn': config.OGRN if config.OGRN else '',
        'ogrnip': config.OGRNIP if config.OGRNIP else ''
    }


class LegalListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/legal_list.html', legals=LegalInfo.query().fetch())


class AddLegalListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/add_legal.html')

    def post(self):
        legal = LegalInfo()
        legal.name = self.request.get('company_name')
        legal.address = self.request.get('company_address')
        legal.site = self.request.get('site')
        legal.person_ooo = self.request.get('legal_person')
        legal.person_ip = self.request.get('legal_person_ip')
        legal.contacts = self.request.get('legal_contacts')
        legal.email = self.request.get('legal_email')
        legal.inn = self.request.get('inn')
        legal.kpp = self.request.get('kpp')
        legal.ogrn = self.request.get('ogrn')
        legal.ogrnip = self.request.get('ogrnip')
        legal.put()
        self.redirect('/company/docs/about')


class EditLegalHandler(CompanyBaseHandler):
    def get(self):
        legal_id = self.request.get_range('legal_id')
        legal = LegalInfo.get_by_id(legal_id)
        if not legal:
            self.abort(400)
        self.render('/docs/add_legal.html', legal=legal)

    def post(self):
        legal_id = self.request.get_range('legal_id')
        legal = LegalInfo.get_by_id(legal_id)
        if not legal:
            self.abort(400)
        legal.name = self.request.get('company_name')
        legal.address = self.request.get('company_address')
        legal.site = self.request.get('site')
        legal.person_ooo = self.request.get('legal_person')
        legal.person_ip = self.request.get('legal_person_ip')
        legal.contacts = self.request.get('legal_contacts')
        legal.email = self.request.get('legal_email')
        legal.inn = self.request.get('inn')
        legal.kpp = self.request.get('kpp')
        legal.ogrn = self.request.get('ogrn')
        legal.ogrnip = self.request.get('ogrnip')
        legal.put()
        self.redirect('/company/docs/about')


class AboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        values = _get_values()
        namespace = namespace_manager.get_namespace()
        values.update({
            'licence_url': u'http://%s.1.%s/docs/licence_agreement.html' % (namespace, urlparse(self.request.url).hostname),
            'payment_rules_url': u'http://%s.1.%s/docs/payment_rules.html' % (namespace, urlparse(self.request.url).hostname),
            'paypal_privacy_policy_url': u'http://%s.1.%s/docs/paypal_privacy_policy.html' % (namespace, urlparse(self.request.url).hostname),
            'paypal_user_agreement_url': u'http://%s.1.%s/docs/paypal_user_agreement.html' % (namespace, urlparse(self.request.url).hostname),
        })
        self.render('/docs/about.html', **values)


class SetAboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/set_about.html', **_get_values())

    @company_user_required
    def post(self):
        config = Config.get()
        config.APP_NAME = self.request.get('name')
        config.COMPANY_DESCRIPTION = self.request.get('info')
        config.COMPANY_NAME = self.request.get('company_name')
        config.COMPANY_ADDRESS = self.request.get('company_address')
        config.SUPPORT_PHONE = self.request.get('phone')
        config.SUPPORT_SITE = self.request.get('site')
        config.SUPPORT_EMAILS = self.request.get('emails').split(',')
        config.DELIVERY_PHONES = self.request.get('delivery_phones').split(',') if self.request.get('delivery_phones') else []
        config.DELIVERY_EMAILS = self.request.get('delivery_emails').split(',') if self.request.get('delivery_emails') else []
        config.LEGAL_PERSON = self.request.get('legal_person')
        config.LEGAL_PERSON_IP = self.request.get('legal_person_ip')
        config.LEGAL_CONTACTS = self.request.get('legal_contacts')
        config.LEGAL_EMAIL = self.request.get('legal_email')
        config.INN = self.request.get('inn')
        config.KPP = self.request.get('kpp')
        config.OGRN = self.request.get('ogrn')
        config.OGRNIP = self.request.get('ogrnip')
        config.put()
        self.redirect('/company/docs/about')