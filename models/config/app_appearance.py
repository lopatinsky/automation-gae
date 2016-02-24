__author__ = 'ivanoschepkov'

from google.appengine.ext import ndb

class AppAppearanceIos(ndb.Model):
    base_color = ndb.StringProperty(indexed=False, default='FF000000')

    base_text_color = ndb.StringProperty(indexed=False, default='FF000000')
    additional_text_color = ndb.StringProperty(indexed=False, default='FF000000')

    error_color = ndb.StringProperty(indexed=False, default='FF000000')

    topbar_color = ndb.StringProperty(indexed=False, default='FF000000')
    topbar_text_color = ndb.StringProperty(indexed=False, default='FF000000')

    menu_header_color = ndb.StringProperty(indexed=False, default='FF000000')


    def dict(self):
        return {
            "base_color": self.base_color,
            "base_text_color": self.base_text_color,
            "additional_text_color": self.additional_text_color,
            "error_color": self.error_color,
            "topbar_color": self.topbar_color,
            "topbar_text_color": self.topbar_text_color,
            "menu_header_color": self.menu_header_color
        }

class AppAppearanceAndroid(ndb.Model):
    base_color = ndb.StringProperty(indexed=False, default='FF000000')

    base_text_color = ndb.StringProperty(indexed=False, default='FF000000')
    additional_text_color = ndb.StringProperty(indexed=False, default='FF000000')

    error_color = ndb.StringProperty(indexed=False, default='FF000000')

    toolbar_color = ndb.StringProperty(indexed=False, default='FF000000')
    topbar_color = ndb.StringProperty(indexed=False, default='FF000000')
    topbar_text_color = ndb.StringProperty(indexed=False, default='FF000000')


    def dict(self):
        return {
            "base_color": self.base_color,
            "base_text_color": self.base_text_color,
            "additional_text_color": self.additional_text_color,
            "error_color": self.error_color,
            "toolbar_color": self.toolbar_color,
            "topbar_color": self.topbar_color,
            "topbar_text_color": self.topbar_text_color
        }