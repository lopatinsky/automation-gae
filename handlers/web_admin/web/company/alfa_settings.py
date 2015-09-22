from models.config.config import config, Config
from handlers.web_admin.web.company.base import CompanyBaseHandler
from models.legal import LegalInfo


class AlfaSettingsHandler(CompanyBaseHandler):
    def get(self):
        legals = LegalInfo.query().fetch()
        alfa_production = 'test' not in config.ALFA_BASE_URL
        self.render('/alfa.html',
                    legals=legals,
                    production=alfa_production,
                    bind_login=config.ALFA_LOGIN,
                    bind_password=config.ALFA_PASSWORD)

    def post(self):
        cfg = Config.get()
        cfg.ALFA_BASE_URL = 'https://engine.paymentgate.ru/payment' if self.request.get('alfa') == 'production' \
            else 'https://test.paymentgate.ru/testpayment'
        cfg.ALFA_LOGIN = self.request.get('bind_login')
        cfg.ALFA_PASSWORD = self.request.get('bind_password')
        cfg.put()

        legals = LegalInfo.query().fetch()
        for legal in legals:
            legal.alfa_login = self.request.get('login_%s' % legal.key.id())
            legal.alfa_password = self.request.get('password_%s' % legal.key.id())
            legal.put()
        self.redirect('/company/main')
