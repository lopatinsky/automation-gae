from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from config import Config
from handlers.maintenance.base import BaseHandler

__author__ = 'dvpermyakov'


class EmailsErrorsHandler(BaseHandler):
    def get(self):
        response = ''
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            if not config:
                continue
            if config.SEND_ERRORS_500:
                response += '%s, ' % namespace
        self.response.write(response)