from google.appengine.api.namespace_manager import namespace_manager

from base import CompanyBaseHandler
from methods.auth import full_rights_required
from models.config.config import config, Config
from models.config.version import CURRENT_VERSION, CURRENT_APP_ID
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
        'in_production': config.IN_PRODUCTION,
    }


class LegalListHandler(CompanyBaseHandler):
    @full_rights_required
    def get(self):
        namespace = namespace_manager.get_namespace()
        host = u'http://%s.%s.%s.appspot.com' % (namespace, CURRENT_VERSION, CURRENT_APP_ID)
        values = {
            'licence_url': u'%s/docs/licence_agreement.html' % host,
            'payment_rules_url': u'%s/docs/payment_rules.html' % host,
            'paypal_privacy_policy_url': u'%s/docs/paypal_privacy_policy.html' % host,
            'paypal_user_agreement_url': u'%s/docs/paypal_user_agreement.html' % host,
        }
        self.render('/docs/legal_list.html', legals=LegalInfo.query().fetch(), **values)


class AddLegalListHandler(CompanyBaseHandler):
    @full_rights_required
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
        legal.report_emails = self.request.get('report_emails')
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
        legal.report_emails = self.request.get('report_emails')
        legal.put()
        self.redirect('/company/docs/legal/list')


class AboutCompanyHandler(CompanyBaseHandler):
    @full_rights_required
    def get(self):
        self.render('/docs/about.html', **_get_values())


class SetAboutCompanyHandler(CompanyBaseHandler):
    @full_rights_required
    def get(self):
        self.render('/docs/set_about.html', **_get_values())

    @full_rights_required
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
        config.IN_PRODUCTION = bool(self.request.get('in_production'))
        config.put()
        self.redirect('/company/docs/about')
