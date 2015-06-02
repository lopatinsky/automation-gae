from ..base import CompanyBaseHandler
from methods.excel import parsing

__author__ = 'dvpermyakov'


class ParseMenuHandler(CompanyBaseHandler):
    def post(self):
        excel = self.request.get('excel')
        parsing.menu_parse(excel)
        self.redirect('/company/menu/main')