# coding=utf-8
from datetime import datetime, timedelta
import logging
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.api.taskqueue import taskqueue
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.rendering import HTML_STR_TIME_FORMAT
from models import News, Notification, Venue
from models.specials import Channel, CATEGORY_CHANNEL, VENUE_CHANNEL

__author__ = 'dvpermyakov'

MAX_SECONDS_LOSS = 30


class ListNewsHandler(CompanyBaseHandler):
    def get(self):
        news = News.query().order(-News.start).fetch()
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


class PushesListHandler(CompanyBaseHandler):
    def get(self):
        pushes = Notification.query().order(-Notification.start).fetch()
        self.render('/notifications/pushes_list.html', pushes=pushes)


class AddPushesHandler(CompanyBaseHandler):
    def get(self):
        values = {
            'venues': Venue.query(Venue.active == True).fetch()
        }
        self.render('/notifications/pushes_add.html', **values)

    def post(self):
        def error(description):
            self.render('/notifications/pushes_add.html', error=description)

        text = self.request.get('text')
        if not text:
            return error(u'Введите текст')
        header = self.request.get('header')
        if not header:
            return error(u'Введите заголовок')
        full_text = self.request.get('full_text')
        if not full_text:
            return error(u'Введите полный текст')
        start = self.request.get('start')
        if start:
            try:
                start = datetime.strptime(start, HTML_STR_TIME_FORMAT)
            except:
                return error(u'Неверное время отправки')
        else:
            return error(u'Введите время отправки')
        channels = []
        if self.request.get('company'):
            channels.append(Channel(name=u'Всем', channel=namespace_manager.get_namespace()))
        for venue in Venue.query(Venue.active == True).fetch():
            if self.request.get(str(venue.key.id())):
                channels.append(Channel(name=venue.title, channel=VENUE_CHANNEL % venue.key.id()))
        notification = Notification(start=start, text=text, popup_text=full_text, header=header, channels=channels)
        notification.put()
        taskqueue.add(url='/task/pushes/start', method='POST', eta=start, params={
            'notification_id': notification.key.id()
        })
        self.redirect('/company/notifications/pushes/list')