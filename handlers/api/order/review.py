# coding=utf-8
import logging

from handlers.api.base import ApiHandler
from methods.emails import postmark
from models import Venue
from models.client import Client
from models.config import config
from models.order import OrderRate, Order

__author__ = 'dvpermyakov'


class OrderReviewHandler(ApiHandler):
    def post(self):
        client_id = int(self.request.headers.get('Client-Id') or 0)
        client = Client.get(client_id)
        if not client:
            self.abort(400)
        order_id = self.request.get_range('order_id')
        order = Order.get_by_id(order_id)
        if order.client_id != client.key.id():
            self.abort(409)
        meal_rate = float(self.request.get('meal_rate'))
        service_rate = float(self.request.get('service_rate'))
        comment = self.request.get('comment')
        rate = OrderRate(meal_rate=meal_rate, service_rate=service_rate, comment=comment)
        order.rate = rate
        order.put()

        is_negative = 0 < meal_rate < 4 or 0 < service_rate < 4

        if is_negative or rate.comment:
            conf = config.Config.get()

            venue = Venue.get(order.venue_id)

            emails = conf.SUPPORT_EMAILS
            body = u"Клиент: {0} {1}<br>" \
                   u"Заказ: {2}<br>" \
                   u"Точка: {3}<br>" \
                   u"Оценка еды: {4} из 5<br>" \
                   u"Оценка обслуживания: {5} из 5<br>" \
                   .format(client.tel, client.name, order.number, venue.title, meal_rate, service_rate)

            if comment:
                body += u"Комментарий: %s" % comment
            logging.info(body)
            to = emails
            cc = ['mdburshteyn@gmail.com', 'elenamarchenko.lm@gmail.com']
            subject = u'Негативный отзыв о заказе' if is_negative else u'Отзыв о заказе с комментарием'
            postmark.send_email('noreply-rating@ru-beacon.ru', to, subject, body, cc_email=cc)

        self.render_json({})
