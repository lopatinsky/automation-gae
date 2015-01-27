# -*- coding: utf-8 -*-

__author__ = 'dvpermyakov'

from webapp2 import RequestHandler
from models import Client, Order, Notification, PUSH_NOTIFICATION, SMS_NOTIFICATION
from methods import email, empatika_promos
from datetime import datetime, timedelta
from methods.push import send_reminder_push
from methods.sms import send_sms
from webapp2_extras import jinja2
import logging


class FullyInactiveClientsHandler(RequestHandler):
    def get(self):
        clients_with_phone = Client.query(Client.created > datetime.now() - timedelta(days=1)).fetch()
        for client in clients_with_phone[:]:
            if not client.tel:
                clients_with_phone.remove(client)
        for client in clients_with_phone[:]:
            last_order = Order.query(Order.client_id == client.key.id()).get()
            if last_order:
                clients_with_phone.remove(client)
        if not len(clients_with_phone):
            return
        else:
            body = 'Clients who bind telephone and not order anything:\n'
            for client in clients_with_phone:
                body += 'Name: %s %s, email: %s, telephone: %s\n' % (client.name, client.surname,
                                                                     client.email, client.tel)
            logging.info(body)
            html_file = jinja2.get_jinja2(app=self.app).render_template('inactive_clients.html',
                                                                        clients=clients_with_phone)
            email.send_error('analytics', 'Clients with telephones', body="",  html=html_file)
            for client in clients_with_phone:
                sms_text = (u"%s, добрый день! Спасибо, что скачали приложение Даблби. "
                            u"Теперь можно получить кофе без очереди в кассу. "
                            u"А если у Вас MasterCard, Вас ждут дополнительные подарки. "
                            u"Хорошего дня!") % client.name
                send_sms("DoubleB", [client.tel], sms_text)
                notification = Notification(client_id=client.key.id(), type=SMS_NOTIFICATION)
                notification.put()


class SeveralDaysInactiveClientsHandler(RequestHandler):
    WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    WEEK_OF_INACTIVE_DAYS = {
        'monday': [6, 5],
        'tuesday': [5],
        'wednesday': [5],
        'friday': [4, 5, 6]
    }

    def get(self):
        orders = []
        for inactive_days in self.WEEK_OF_INACTIVE_DAYS[self.WEEK[datetime.today().weekday()]]:
            orders.extend(Order.query(Order.date_created > datetime.now() - timedelta(days=inactive_days),
                                      Order.date_created < datetime.now() - timedelta(days=inactive_days - 1)).fetch())
        clients_id = []
        for order in orders:
            if not order.client_id in clients_id:
                clients_id.append(order.client_id)
        orders = []
        for inactive_days in self.WEEK_OF_INACTIVE_DAYS[self.WEEK[datetime.today().weekday()]]:
            orders.extend(Order.query(Order.date_created > datetime.now() - timedelta(days=inactive_days - 1)).fetch())

        for order in orders:
            if order.client_id in clients_id:
                clients_id.remove(order.client_id)
        for client_id in clients_id:
            client = Client.get_by_id(client_id)
            score = empatika_promos.get_user_points(client.key.id()) % 5
            name = client.name if client.name_confirmed else None
            send_reminder_push(client_id, name, score)
            notification = Notification(client_id=client_id, type=PUSH_NOTIFICATION)
            notification.put()