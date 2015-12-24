from google.appengine.ext import ndb

__author__ = 'Artem'

STATUSES = ['Failed', 'Active', 'Completed']


class _AE_DatastoreAdmin_Operation(ndb.Model):
    status = ndb.StringProperty()
    active_jobs = ndb.IntegerProperty(default=0)
    completed_jobs = ndb.IntegerProperty()
    description = ndb.StringProperty()
    last_updated = ndb.DateTimeProperty()