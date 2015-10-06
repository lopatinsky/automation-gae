from google.appengine.api.namespace_manager import namespace_manager
from ..base import ApiHandler
from models import STATUS_AVAILABLE
from models.proxy.unified_app import AutomationCompany


class CompaniesHandler(ApiHandler):
    def get(self):
        if self.request.init_namespace:
            namespace_manager.set_namespace(self.request.init_namespace)
        self.render_json({
            'companies': [company.dict()
                          for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch()]
        })
