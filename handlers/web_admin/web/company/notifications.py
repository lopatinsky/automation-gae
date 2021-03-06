# coding=utf-8
from datetime import datetime, timedelta

from google.appengine.api import namespace_manager

from google.appengine.api.taskqueue import taskqueue

from models.config.config import Config
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.auth import news_rights_required, pushes_rights_required, full_rights_required
from methods.rendering import HTML_STR_TIME_FORMAT, STR_DATETIME_FORMAT
from models import News, Notification, Venue
from models.specials import Channel, COMPANY_CHANNEL, VENUE_CHANNEL, NOTIFICATION_STATUS_MAP, STATUS_CREATED, \
    STATUS_ACTIVE, get_channels
from methods.images import get_new_image_url

__author__ = 'dvpermyakov'

MAX_SECONDS_LOSS = 30


class ListNewsHandler(CompanyBaseHandler):
    @news_rights_required
    def get(self):
        news = News.query().order(-News.start).fetch()
        for new in news:
            new.created_str = new.created.strftime(STR_DATETIME_FORMAT)
        utc_time = datetime.utcnow().strftime(STR_DATETIME_FORMAT)
        self.render('/notifications/news_list.html', news=news, utc_time=utc_time,
                    NOTIFICATION_STATUS_MAP=NOTIFICATION_STATUS_MAP,
                    STATUS_ACTIVE=STATUS_ACTIVE, STATUS_CREATED=STATUS_CREATED)


class AddNewsHandler(CompanyBaseHandler):
    @news_rights_required
    def get(self):
        self.render('/notifications/news_add.html')

    @news_rights_required
    def post(self):
        def error(description):
            self.render('/notifications/news_add.html', error=description)

        title = self.request.get('title')

        if not title:
            return error(u'Введите заголовок')

        text = self.request.get('text')
        if not text:
            return error(u'Введите текст')
        image_url = self.request.get('image_url')

        send_now = bool(self.request.get('send_now'))
        if send_now:
            start = datetime.utcnow()
        else:
            start = self.request.get('start')
            if start:
                try:
                    start = datetime.strptime(start, HTML_STR_TIME_FORMAT)
                except ValueError:
                    return error(u'Неверное время начала')
            else:
                return error(u'Введите время начала')
            if start < datetime.utcnow():
                return error(u'Введите время больше текущего в utc')

        notification = None
        if self.request.get('send_push'):
            channels = []
            company_namespace = namespace_manager.get_namespace()

            company_channel = get_channels(company_namespace)[COMPANY_CHANNEL]
            channels.append(Channel(name=u'Всем', channel=company_channel))
            for venue in Venue.query(Venue.active == True).fetch():
                if self.request.get(str(venue.key.id())):
                    venue_channel = get_channels(company_namespace)[VENUE_CHANNEL]
                    channels.append(Channel(name=venue.title, channel=venue_channel))
            notification = Notification(start=start, text=text, header=title, channels=channels,
                                    should_popup=False)

        news = News(text=text, title=title, image_url=image_url, start=start, notification=notification)

        news.put()
        new_url = get_new_image_url('News', news.key.id(), url=image_url)
        if new_url:
            news.image_url = new_url
            news.put()
        taskqueue.add(url='/task/news/start', method='POST', eta=start, params={
            'news_id': news.key.id()
        })
        self.redirect('/company/notifications/news/list')


class CancelNewsHandler(CompanyBaseHandler):
    @news_rights_required
    def post(self):
        news_id = self.request.get_range('news_id')
        news = News.get_by_id(news_id)
        if not news:
            self.abort(400)
        if news.status in [STATUS_CREATED, STATUS_ACTIVE]:
            news.cancel()
            self.render_json({
                'success': True,
                'news_id': news_id,
                'status_str': NOTIFICATION_STATUS_MAP[news.status]
            })
        else:
            self.render_json({
                'success': False
            })


class PushesListHandler(CompanyBaseHandler):
    @pushes_rights_required
    def get(self):
        pushes = Notification.query().order(-Notification.start).fetch()
        for push in pushes:
            push.created_str = push.created.strftime(STR_DATETIME_FORMAT)
        utc_time = datetime.utcnow().strftime(STR_DATETIME_FORMAT)
        self.render('/notifications/pushes_list.html', pushes=pushes, utc_time=utc_time,
                    PUSH_STATUS_MAP=NOTIFICATION_STATUS_MAP, STATUS_CREATED=STATUS_CREATED)


class AddPushesHandler(CompanyBaseHandler):
    def render_template(self, error=None):
        values = {
            'venues': Venue.query(Venue.active == True).fetch(),
            'error': error
        }
        self.render('/notifications/pushes_add.html', **values)

    @pushes_rights_required
    def get(self):
        self.render_template()

    @pushes_rights_required
    def post(self):
        def error(description):
            return self.render_template(description)

        text = self.request.get('text')
        if not text:
            return error(u'Введите текст')
        header = self.request.get('header')
        if not header:
            return error(u'Введите заголовок')
        full_text = self.request.get('full_text')
        if not full_text:
            return error(u'Введите полный текст')
        send_now = bool(self.request.get('send_now'))
        if send_now:
            start = datetime.utcnow()
        else:
            start = self.request.get('start')
            if start:
                try:
                    start = datetime.strptime(start, HTML_STR_TIME_FORMAT)
                except ValueError:
                    return error(u'Неверное время отправки')
            else:
                return error(u'Введите время отправки')
        if not send_now and start < datetime.utcnow() + timedelta(seconds=MAX_SECONDS_LOSS):
            return error(u'Введите время больше текущего в utc')
        channels = []
        company_namespace = namespace_manager.get_namespace()
        if self.request.get('company'):
            company_channel = get_channels(company_namespace)[COMPANY_CHANNEL]
            channels.append(Channel(name=u'Всем', channel=company_channel))
        for venue in Venue.query(Venue.active == True).fetch():
            if self.request.get(str(venue.key.id())):
                venue_channel = get_channels(company_namespace)[VENUE_CHANNEL]
                channels.append(Channel(name=venue.title, channel=venue_channel))
        notification = Notification(start=start, text=text, popup_text=full_text, header=header, channels=channels,
                                    should_popup=True)

        notification.put()
        taskqueue.add(url='/task/pushes/start', method='POST', eta=start, params={
            'notification_id': notification.key.id()
        })

        self.redirect('/company/notifications/pushes/list')



class CancelPushHandler(CompanyBaseHandler):
    @pushes_rights_required
    def post(self):
        notification_id = self.request.get_range('notification_id')
        notification = Notification.get_by_id(notification_id)
        if not notification:
            self.abort(400)
        if notification.status == STATUS_CREATED:
            notification.cancel()
            self.render_json({
                'success': True,
                'notification_id': notification_id,
                'status_str': NOTIFICATION_STATUS_MAP[notification.status]
            })
        else:
            self.render_json({
                'success': False
            })


class ChangeParseApiKeys(CompanyBaseHandler):
    @full_rights_required
    def get(self):
        self.render('/notifications/parse_api_keys.html')

    @full_rights_required
    def post(self):
        config = Config.get()
        config.PARSE_APP_API_KEY = self.request.get('app_key')
        config.PARSE_CLIENT_API_KEY = self.request.get('client_key')
        config.PARSE_REST_API_KEY = self.request.get('rest_key')
        config.put()
        self.redirect('/company/notifications/pushes/list')
