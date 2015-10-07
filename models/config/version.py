# coding=utf-8
from google.appengine.api import app_identity, modules
from google.appengine.ext import ndb

__author__ = 'dvpermyakov'

CURRENT_APP_ID = app_identity.get_application_id()
DEMO_APP_ID = 'automation-demo'
PRODUCTION_APP_ID = 'doubleb-automation-production'
CURRENT_VERSION = modules.get_current_version_name()
TEST_VERSIONS = ('test2', 'p-test', 'courier')


class Version(ndb.Model):
    created = ndb.DateTimeProperty(required=True)
    updated = ndb.DateTimeProperty(required=True)
    number = ndb.IntegerProperty()
    available = ndb.BooleanProperty(default=True)
    force = ndb.BooleanProperty(default=False)

    def dict(self):
        return {
            'text': u'Обновите приложение!',
            'force': self.force
        }
