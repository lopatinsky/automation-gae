from google.appengine.api.namespace_manager import namespace_manager
from ..base import ApiHandler
from config import config
from models import STATUS_AVAILABLE
from models.proxy.unified_app import AutomationCompany


class CompaniesHandler(ApiHandler):
    def get(self):
        companies = AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch()
        company_dicts = []
        for company in companies:
            namespace_manager.set_namespace(company.namespace)
            company_dicts.append({
                'namespace': company.namespace,
                'name': config.APP_NAME
            })
        self.render_json({
            'companies': company_dicts
        })