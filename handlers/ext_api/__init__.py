from google.appengine.api import namespace_manager
from google.appengine.ext.ndb import metadata
from .base import GAEAuthBaseHandler
from models.config.config import config, COMPANY_IN_PRODUCTION
from models.legal import LegalInfo


class ExportLegalsHandler(GAEAuthBaseHandler):
    ALLOWED_IDS = "rubeacon-legals",

    def get(self):
        result = []
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            for legal in LegalInfo.query().fetch():
                result.append({
                    'id': [namespace, legal.key.id()],
                    'app_name': config.APP_NAME or "",
                    'name': legal.person_ooo or legal.person_ip,
                    'production': config.COMPANY_STATUS == COMPANY_IN_PRODUCTION,
                })
        self.render_json({"legals": result})
