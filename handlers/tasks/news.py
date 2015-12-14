from webapp2 import RequestHandler
from models import News
from models.client import ANDROID_DEVICE, IOS_DEVICE
from models.push import NewsPush
from models.specials import STATUS_CREATED, STATUS_ACTIVE

__author__ = 'dvpermyakov'


class StartNewsHandler(RequestHandler):
    def post(self):
        news_id = self.request.get_range('news_id')
        news = News.get_by_id(news_id)
        if not news:
            self.abort(400)
        if news.status == STATUS_CREATED:
            news.activate()

        if news.notification is not None:
            self.send_notification(news=news)
            pass

    def send_notification(self, news):
        notification = news.notification
        if not notification:
            self.abort(400)
        if notification.status == STATUS_CREATED:
            channels = []
            for channel in notification.channels:
                channels.append(channel.channel)

            android_push = NewsPush(news=news, channels=channels, device_type=ANDROID_DEVICE)
            ios_push = NewsPush(news=news, channels=channels, device_type=IOS_DEVICE)

            android_push.send()
            ios_push.send()


class CloseNewsHandler(RequestHandler):
    def post(self):
        news_id = self.request.get_range('news_id')
        news = News.get_by_id(news_id)
        if not news:
            self.abort(400)
        if news.status == STATUS_ACTIVE:
            news.deactivate()