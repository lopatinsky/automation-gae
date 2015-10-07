from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from models import STATUS_AVAILABLE, STATUS_CHOICES
from models.config.config import Config

__author__ = 'dvpermyakov'


class AutomationCompany(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    namespace = ndb.StringProperty(required=True)
    image = ndb.StringProperty()
    description = ndb.StringProperty()

    def dict(self):
        namespace_manager.set_namespace(self.namespace)
        config = Config.get()
        return {
            'name': config.APP_NAME,
            'namespace': self.namespace,
            'image': self.image,
            'description': self.description
        }
