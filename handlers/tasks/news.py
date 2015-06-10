from webapp2 import RequestHandler
from models import News

__author__ = 'dvpermyakov'


class StartNewsHandler(RequestHandler):
    def post(self):
        news_id = self.request.get_range('news_id')
        news = News.get_by_id(news_id)
        if not news:
            self.abort(400)
        news.activate()


class CloseNewsHandler(RequestHandler):
    def post(self):
        news_id = self.request.get_range('news_id')
        news = News.get_by_id(news_id)
        if not news:
            self.abort(400)
        news.deactivate()