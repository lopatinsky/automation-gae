__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class TabletRequest(ndb.Model):
    admin_id = ndb.IntegerProperty(required=True, indexed=False)
    token = ndb.StringProperty(required=True, indexed=False)
    request_time = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    location = ndb.GeoPtProperty()
    error_number = ndb.IntegerProperty(default=0, indexed=False)
    sound_level = ndb.IntegerProperty(required=True, indexed=False)
    is_in_charging = ndb.BooleanProperty(default=False, indexed=False)
    is_turned_on = ndb.BooleanProperty(default=True, indexed=False)
    app_version = ndb.StringProperty(required=True, indexed=False)