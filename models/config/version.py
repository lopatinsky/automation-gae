# coding=utf-8
from google.appengine.ext import ndb

__author__ = 'dvpermyakov'

DEMO_HOSTNAME = u'automation-demo.appspot.com'
PRODUCTION_HOSTNAME = u'doubleb-automation-production.appspot.com'
TEST_VERSIONS = ('.test2.', '.p-test.', '.courier.')


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
