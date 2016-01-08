from google.appengine.api import namespace_manager
from google.appengine.ext.ndb import metadata
from handlers.web_admin.web.company.base import CompanyBaseHandler
from methods.auth import company_user_required
from models.config.config import config


class ChooseNamespaceHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        if "namespace" in self.session:
            del self.session["namespace"]
        namespaces = metadata.get_namespaces()
        real_namespaces = []
        for namespace in namespaces:
            namespace_manager.set_namespace(namespace)
            if config and config.APP_NAME:
                real_namespaces.append((namespace, config.APP_NAME))
        namespace_manager.set_namespace(None)
        self.render('/choose_namespace.html', namespaces=real_namespaces)

    @company_user_required
    def post(self):
        self.session["namespace"] = self.request.get("namespace")
        self.redirect_to("company_main")
