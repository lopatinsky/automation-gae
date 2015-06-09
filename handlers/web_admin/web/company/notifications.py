# coding=utf-8
from datetime import datetime, timedelta
import logging
from google.appengine.api.taskqueue import taskqueue
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.rendering import HTML_STR_TIME_FORMAT
from models import News

__author__ = 'dvpermyakov'

MAX_SECONDS_LOSS = 30


class ListNewsHandler(CompanyBaseHandler):
    def get(self):
        news = News.query().fetch()
        self.render('/notifications/news_list.html', news=news)


class AddNewsHandler(CompanyBaseHandler):
    def get(self):
        self.render('/notifications/news_add.html')

    def post(self):
        def error(description):
            self.render('/notifications/news_add.html', error=description)

        logging.info(self.request.POST)
        text = self.request.get('text')
        if not text:
            return error(u'Введите текст')
        image_url = self.request.get('image_url')
        if not image_url:
            return error(u'Введите url для картинки')
        start = self.request.get('start')
        end = self.request.get('end')
        if start:
            try:
                start = datetime.strptime(start, HTML_STR_TIME_FORMAT)
            except:
                return error(u'Неверное время начала')
        else:
            return error(u'Введите время начала')
        if end:
            try:
                end = datetime.strptime(end, HTML_STR_TIME_FORMAT)
            except:
                return error(u'Неверное время начала')
        else:
            return error(u'Введите время начала')
        if start < datetime.utcnow() + timedelta(seconds=MAX_SECONDS_LOSS):
            return error(u'Введите время больше текущего в utc')
        if start > end:
            return error(u'Время закрытия должно быть больше времени начала')
        news = News(text=text, image_url=image_url, start=start, end=end)
        news.put()
        taskqueue.add(url='/task/news/start', method='POST', eta=start, params={
            'news_id': news.key.id()
        })
        taskqueue.add(url='/task/news/close', method='POST', eta=end, params={
            'news_id': news.key.id()
        })
        self.redirect('/company/notifications/news/list')