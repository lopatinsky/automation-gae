from ..base import ApiHandler
from models import STATUS_AVAILABLE
from models.proxy.unified_app import AutomationCompany


class CompaniesHandler(ApiHandler):
    def get(self):
        self.render_json({
            'companies': [company.dict()
                          for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch()]
        })
