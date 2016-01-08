from google.appengine.ext import ndb
from models.config.config import AUTO_APP, RESTO_APP

__author__ = 'dvpermyakov'


class CompanyInfo(ndb.Model):
    APP_NAME = ndb.StringProperty(indexed=False)
    COMPANY_DESCRIPTION = ndb.StringProperty(indexed=False)  # suitable name is APP_DESCRIPTION
    SUPPORT_PHONE = ndb.StringProperty(indexed=False)
    SUPPORT_SITE = ndb.StringProperty(indexed=False)
    SUPPORT_EMAILS = ndb.StringProperty(indexed=False, repeated=True)
    ADDITION_INFO_ABOUT_DELIVERY = ndb.StringProperty(indexed=False)
    ANOTHER_CITY_IN_LIST = ndb.BooleanProperty(default=False)

    def get_company_dict(self):
        from methods.proxy.resto.company import get_company_info_dict
        from models.config.config import config
        if config.APP_KIND == AUTO_APP:
            return {
                'app_name': self.APP_NAME,
                'description': self.COMPANY_DESCRIPTION,
                'phone': self.SUPPORT_PHONE,
                'site': self.SUPPORT_SITE,
                'emails': self.SUPPORT_EMAILS
            }
        elif config.APP_KIND == RESTO_APP:
            return get_company_info_dict()
