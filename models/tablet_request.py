__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class TabletRequest(ndb.Model):
    admin_id = ndb.IntegerProperty(required=True, indexed=True)
    token = ndb.StringProperty(required=True, indexed=False)
    request_time = ndb.DateTimeProperty(auto_now_add=True)
    location = ndb.GeoPtProperty(indexed=False)
    error_number = ndb.IntegerProperty(indexed=False)
    sound_level_general = ndb.IntegerProperty(indexed=False)
    sound_level_system = ndb.IntegerProperty(indexed=False)
    is_in_charging = ndb.BooleanProperty(indexed=False)
    is_turned_on = ndb.BooleanProperty(indexed=False)
    app_version = ndb.StringProperty(indexed=False)
    battery_level = ndb.IntegerProperty(indexed=False)
