__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class TabletRequest(ndb.Model):
    admin_id = ndb.IntegerProperty(required=True)
    token = ndb.StringProperty(required=True)
    request_time = ndb.DateTimeProperty(auto_now_add=True)
    location = ndb.GeoPtProperty()