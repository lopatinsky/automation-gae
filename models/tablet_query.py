__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class TabletQuery(ndb.Model):
    admin_id = ndb.IntegerProperty(required=True)
    token = ndb.StringProperty(required=True)
    query_time = ndb.DateTimeProperty(auto_now_add=True)
    location = ndb.GeoPtProperty()