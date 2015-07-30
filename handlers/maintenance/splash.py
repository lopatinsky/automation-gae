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
        icon_link = get_new_image_url('SmartBanner', icon_url, url=icon_url)
        values = {
            'itunes_id': self.request.get('itunes_id'),
            'google_play_id': self.request.get('google_play_id'),
            'title': self.request.get('title'),
            'icon_link': icon_link
        }
        self.render('/splash/smartbanner.html', **values)
