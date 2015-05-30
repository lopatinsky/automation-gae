from urlparse import urlparse
from google.appengine.api.namespace_manager import namespace_manager
from base import CompanyBaseHandler
from methods.auth import company_user_required
from config import config, Config

__author__ = 'dvpermyakov'


def _get_values():
    return {
        'name': config.APP_NAME if config.APP_NAME else '',
        'info': config.COMPANY_DESCRIPTION if config.COMPANY_DESCRIPTION else '',
        'company_name': config.COMPANY_NAME if config.COMPANY_NAME else '',
        'company_address': config.COMPANY_ADDRESS if config.COMPANY_ADDRESS else '',
        'phone': config.SUPPORT_PHONE if config.SUPPORT_PHONE else '',
        'site': config.SUPPORT_SITE if config.SUPPORT_SITE else '',
        'emails': u''.join(config.SUPPORT_EMAILS),
        'delivery_phone': config.DELIVERY_PHONE if config.DELIVERY_PHONE else '',
        'delivery_emails':  u''.join(config.DELIVERY_EMAILS),
        'legal_person': config.LEGAL_PERSON if config.LEGAL_PERSON else '',
        'legal_contacts': config.LEGAL_CONTACTS if config.LEGAL_CONTACTS else '',
        'legal_email': config.LEGAL_EMAIL if config.LEGAL_EMAIL else '',
        'inn': config.INN if config.INN else '',
        'kpp': config.KPP if config.KPP else '',
        'ogrn': config.OGRN if config.OGRN else ''
    }


class AboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        values = _get_values()
        namespace = namespace_manager.get_namespace()
        if not namespace:
            namespace = '1'
        values.update({
            'licence_url': u'http://%s.%s/docs/licence_agreement.html' % (namespace, urlparse(self.request.url).hostname),
            'payment_rules_url': u'http://%s.%s/docs/payment_rules.html' % (namespace, urlparse(self.request.url).hostname)
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
        config.DELIVERY_PHONE = self.request.get('delivery_phone')
        config.DELIVERY_EMAILS = self.request.get('delivery_emails').split(',')
        config.LEGAL_PERSON = self.request.get('legal_person')
        config.LEGAL_CONTACTS = self.request.get('legal_contacts')
        config.LEGAL_EMAIL = self.request.get('legal_email')
        config.INN = self.request.get('inn')
        config.KPP = self.request.get('kpp')
        config.OGRN = self.request.get('ogrn')
        config.put()
        self.redirect('/company/docs/about')