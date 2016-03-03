# coding=utf-8
from google.appengine.ext import ndb, deferred

from methods.emails.postmark import send_email
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.client import Client


class SushinSonEmailModule(ndb.Model):
    status = ndb.IntegerProperty(indexed=False, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    emails = ndb.StringProperty(indexed=False, repeated=True)

    def send(self, order, jinja2):
        from handlers.web_admin.web.company.delivery.orders import order_items_values
        from models.config.config import EMAIL_FROM

        client = Client.get(order.client_id)

        item_values = order_items_values(order)
        subject = u'Новый заказ №%s поступил в систему из мобильного приложения' % order.key.id()

        rendered_body = jinja2.render_template('/company/delivery/sushinson.html', client=client, **item_values)
        for email in self.emails:
            deferred.defer(send_email, EMAIL_FROM, email, subject, rendered_body)
