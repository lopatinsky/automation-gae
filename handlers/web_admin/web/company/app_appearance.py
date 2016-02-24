__author__ = 'ivanoschepkov'

from base import CompanyBaseHandler
from methods.auth import company_info_rights_required
from models.config.config import Config
from models.config.app_appearance import AppAppearanceIos, AppAppearanceAndroid
import logging


def _get_ios_values():
    config = Config.get()
    appearance = config.GET_APP_APPEARANCE_IOS

    return {
        'base_color': appearance.base_color,
        'base_text_color': appearance.base_text_color,
        'additional_text_color': appearance.additional_text_color,
        'error_color': appearance.error_color,
        'topbar_color': appearance.topbar_color,
        'topbar_text_color': appearance.topbar_text_color,
        'menu_header_color': appearance.menu_header_color,
    }

def _get_android_values():
    config = Config.get()
    appearance = config.GET_APP_APPEARANCE_ANDROID

    return {
        'base_color': appearance.base_color,
        'base_text_color': appearance.base_text_color,
        'additional_text_color': appearance.additional_text_color,
        'error_color': appearance.error_color,
        'topbar_color': appearance.topbar_color,
        'topbar_text_color': appearance.topbar_text_color,
        'toolbar_color': appearance.toolbar_color,
    }


class MainAppAppearanceHandler(CompanyBaseHandler):
    @company_info_rights_required
    def get(self):
        self.render('/config_settings/app_appearance/app_appearance.html')

class SetAppIosAppearanceHandler(CompanyBaseHandler):
    @company_info_rights_required
    def get(self):
        self.render('/config_settings/app_appearance/app_appearance_ios.html', **_get_ios_values())

    @company_info_rights_required
    def post(self):
        logging.info(self.request)
        config = Config.get()
        appearance = config.GET_APP_APPEARANCE_IOS
        appearance.base_color = "FF%s" % self.request.get('base_color')[1:]
        appearance.base_text_color = "FF%s" % self.request.get('base_text_color')[1:]
        appearance.additional_text_color = "FF%s" % self.request.get('additional_text_color')[1:]
        appearance.error_color = "FF%s" % self.request.get('error_color')[1:]
        appearance.topbar_color = "FF%s" % self.request.get('topbar_color')[1:]
        appearance.topbar_text_color = "FF%s" % self.request.get('topbar_text_color')[1:]
        appearance.menu_header_color = "FF%s" % self.request.get('menu_header_color')[1:]
        config.put()
        self.redirect('/company/app_appearance/list')

class SetAppAndroidAppearanceHandler(CompanyBaseHandler):
    @company_info_rights_required
    def get(self):
        self.render('/config_settings/app_appearance/app_appearance_android.html', **_get_android_values())

    @company_info_rights_required
    def post(self):
        logging.info(self.request)
        config = Config.get()
        appearance = config.GET_APP_APPEARANCE_ANDROID
        appearance.base_color = "FF%s" % self.request.get('base_color')[1:]
        appearance.base_text_color = "FF%s" % self.request.get('base_text_color')[1:]
        appearance.additional_text_color = "FF%s" % self.request.get('additional_text_color')[1:]
        appearance.error_color = "FF%s" % self.request.get('error_color')[1:]
        appearance.topbar_color = "FF%s" % self.request.get('topbar_color')[1:]
        appearance.topbar_text_color = "FF%s" % self.request.get('topbar_text_color')[1:]
        appearance.toolbar_color = "FF%s" % self.request.get('toolbar_color')[1:]
        config.put()
        self.redirect('/company/app_appearance/list')