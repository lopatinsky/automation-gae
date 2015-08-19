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
        'phone': config.SUPPORT_PHONE if config.SUPPORT_PHONE else '',
        'site': config.SUPPORT_SITE if config.SUPPORT_SITE else '',
        'emails': u','.join(config.SUPPORT_EMAILS),
        'report_emails': config.REPORT_EMAILS or '',
        'color': config.ACTION_COLOR,
        'email_buttons': config.EMAIL_REQUESTS,
    }


class LegalListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        namespace = namespace_manager.get_namespace()
        values = {
            'licence_url': u'http://%s.1.%s/docs/licence_agreement.html' % (namespace, urlparse(self.request.url).hostname),
            'payment_rules_url': u'http://%s.1.%s/docs/payment_rules.html' % (namespace, urlparse(self.request.url).hostname),
            'paypal_privacy_policy_url': u'http://%s.1.%s/docs/paypal_privacy_policy.html' % (namespace, urlparse(self.request.url).hostname),
            'paypal_user_agreement_url': u'http://%s.1.%s/docs/paypal_user_agreement.html' % (namespace, urlparse(self.request.url).hostname),
        }
        self.render('/docs/legal_list.html', legals=LegalInfo.query().fetch(), **values)


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
        self.redirect('/company/docs/legal/list')


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
        self.render('/docs/about.html', **_get_values())


class SetAboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/set_about.html', **_get_values())

    @company_user_required
    def post(self):
        config = Config.get()
        config.APP_NAME = self.request.get('name')
        config.COMPANY_DESCRIPTION = self.request.get('info')
        config.SUPPORT_PHONE = self.request.get('phone')
        config.SUPPORT_SITE = self.request.get('site')
        config.SUPPORT_EMAILS = self.request.get('emails').split(',')
        config.REPORT_EMAILS = self.request.get('report_emails')
        config.ACTION_COLOR = "FF%s" % self.request.get('color')[1:]
        config.EMAIL_REQUESTS = bool(self.request.get('email_buttons'))
        config.put()
        self.redirect('/company/docs/about')
