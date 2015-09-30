from google.appengine.api import namespace_manager
from google.appengine.ext.ndb import metadata
from .base import GAEAuthBaseHandler
from models.config.config import Config
from models.legal import LegalInfo


class ExportLegalsHandler(GAEAuthBaseHandler):
    ALLOWED_IDS = "rubeacon-legals",

    def get(self):
        result = []
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            cfg = Config.get()
            for legal in LegalInfo.query().fetch():
                result.append({
                    'id': [namespace, legal.key.id()],
                    'app_name': cfg.APP_NAME or "",
                    'name': legal.person_ooo or legal.person_ip
                })
        self.render_json({"legals": result})
