import logging
from base import BaseHandler
from methods.images import get_new_image_url

__author__ = 'dvpermyakov'


class SplashMainHandler(BaseHandler):
    def get(self):
        self.render('/splash/main.html')


class SmartBannerHandler(BaseHandler):
    def get(self):
        self.render('/splash/smartbanner_set_info.html')

    def post(self):
        icon_url = self.request.get('icon_link')
        logging.info(icon_url)
        icon_link = get_new_image_url('SmartBanner', icon_url, url=icon_url)
        values = {
            'itunes_id': self.request.get('itunes_id'),
            'google_play_id': self.request.get('google_play_id'),
            'title': self.request.get('title'),
            'icon_link': icon_link
        }
        self.render('/splash/smartbanner.html', **values)


class SplashScreenHandler(BaseHandler):
    def get(self):
        self.render('/splash/splashcreen_set_info.html')

    def post(self):
        phone = self.request.get('phone')
        logo_url = self.request.get('logo_url')
        logo_url = get_new_image_url('Splash', logo_url, url=logo_url)
        app_url = self.request.get('app_url')
        app_url = get_new_image_url('Splash', app_url, url=app_url)
        rbcn_url = self.request.get('rbcn_url')
        site = self.request.get('site')
        values = {
            'phone': phone,
            'logo_url': logo_url,
            'app_url': app_url,
            'rbcn_url': rbcn_url,
            'site': site
        }
        self.render('/splash/splash_screen.html', **values)