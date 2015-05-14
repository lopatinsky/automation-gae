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
            'info': config.COMPANY_DESCRIPTION
        })


class SetAboutCompanyHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/docs/set_about.html', **{
            'info': config.COMPANY_DESCRIPTION if config.COMPANY_DESCRIPTION else ''
        })

    @company_user_required
    def post(self):
        info = self.request.get('info')
        config = Config.get()
        config.COMPANY_DESCRIPTION = info
        config.put()
        self.redirect('/company/docs/about')