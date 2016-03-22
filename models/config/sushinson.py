# coding=utf-8
from google.appengine.ext import ndb, deferred

from methods.emails.postmark import send_by_smtp
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.client import Client
from models.payment_types import PAYMENT_TYPE_MAP


class SushinSonEmailModule(ndb.Model):
    status = ndb.IntegerProperty(indexed=False, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    emails = ndb.StringProperty(indexed=False, repeated=True)

    def send(self, order, jinja2):
        from handlers.web_admin.web.company.delivery.orders import order_items_values
        from models.config.config import EMAIL_FROM

        client = Client.get(order.client_id)

        item_values = order_items_values(order)
        subject = u'Поступил заказ из приложения'

        rendered_body = jinja2.render_template('/company/delivery/sushinson.html', client=client,
                                               PAYMENT_TYPE_MAP=PAYMENT_TYPE_MAP, **item_values)
        for email in self.emails:
            deferred.defer(send_by_smtp, EMAIL_FROM, email, subject, rendered_body)
