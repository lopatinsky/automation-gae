from base import CompanyBaseHandler
from methods.auth import company_user_required
from config import config, Config

__author__ = 'dvpermyakov'


class ListDocsHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/list.html')


class AboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/about.html', **{
            'info': config.COMPANY_DESCRIPTION if config.COMPANY_DESCRIPTION else '',
            'name': config.APP_NAME if config.APP_NAME else '',
            'phone': config.SUPPORT_PHONE if config.SUPPORT_PHONE else '',
            'site': config.SUPPORT_SITE if config.SUPPORT_SITE else '',
            'emails': u''.join(config.SUPPORT_EMAILS)
        })


class SetAboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/set_about.html', **{
            'info': config.COMPANY_DESCRIPTION if config.COMPANY_DESCRIPTION else '',
            'name': config.APP_NAME if config.APP_NAME else '',
            'phone': config.SUPPORT_PHONE if config.SUPPORT_PHONE else '',
            'site': config.SUPPORT_SITE if config.SUPPORT_SITE else '',
            'emails': u''.join(config.SUPPORT_EMAILS)
        })

    @company_user_required
    def post(self):
        info = self.request.get('info')
        name = self.request.get('name')
        phone = self.request.get('phone')
        site = self.request.get('site')
        emails = self.request.get('emails').split(',')
        config = Config.get()
        config.COMPANY_DESCRIPTION = info
        config.APP_NAME = name
        config.SUPPORT_PHONE = phone
        config.SUPPORT_SITE = site
        config.SUPPORT_EMAILS = emails
        config.put()
        self.redirect('/company/docs/about')