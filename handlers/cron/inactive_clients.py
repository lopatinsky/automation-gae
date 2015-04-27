# -*- coding: utf-8 -*-

__author__ = 'dvpermyakov'

from webapp2 import RequestHandler
from models import Client, Order, Notification, SMS_SUCCESS, CardBindingPayment
from methods import email
from datetime import datetime, timedelta
from methods import sms_pilot
from webapp2_extras import jinja2


class SuccessBindingCardHandler(RequestHandler):
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
            clients_with_card = []
            for client in clients_with_phone:
                if client.tied_card:
                    clients_with_card.append(client)

            for client in clients_with_card:
                sms_text = (u"%s, добрый день! Спасибо, что скачали приложение Даблби. "
                            u"Теперь можно получить кофе без очереди в кассу. "
                            u"А если у Вас MasterCard, Вас ждут дополнительные подарки. "
                            u"Хорошего дня!") % client.name_for_sms
                sms_pilot.send_sms("DoubleB", [client.tel], sms_text)
                notification = Notification(client_id=client.key.id(), type=SMS_SUCCESS)
                notification.put()


class BindingCardHandler(RequestHandler):
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
            clients_with_card = []
            error_clients = []
            passive_clients = []
            for client in clients_with_phone:
                if client.tied_card:
                    clients_with_card.append(client)
                    client.sms = 'Binding card'
                    continue
                attempts = CardBindingPayment.query(CardBindingPayment.client_id == client.key.id()).fetch()
                error = False
                for attempt in attempts:
                    if attempt.success is False:
                        error_clients.append(client)
                        client.sms = 'None (Error binding card)'
                        error = True
                        continue
                if error:
                    continue
                client.sms = 'No try / Cancel binding card'
                passive_clients.append(client)

            html_file = jinja2.get_jinja2(app=self.app).render_template('inactive_clients.html',
                                                                        clients=clients_with_phone)

            email.send_error('analytics', 'Привязка карт', body="",  html=html_file)

            for client in passive_clients:
                sms_text = (u'Доброе утро, %s!\n'
                            u'Спасибо, что пользуетесь приложением Даблби. '
                            u'Привяжите карту и воспользуйтесь 50%% скидкой на первую кружку.\n'
                            u'Хорошего дня,\n'
                            u'Команда Даблби') % client.name
                #twilio.send_sms(receiver_phones=[client.tel], text=sms_text)
                #notification = Notification(client_id=client.key.id(), type=SMS_PASSIVE)
                #notification.put()


class SeveralDaysInactiveClientsHandler(RequestHandler):
    INACTIVE_PERIOD_IN_DAYS = 3 * 7

    WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    WEEK_OF_INACTIVE_DAYS = {
        'monday': [INACTIVE_PERIOD_IN_DAYS],
        'tuesday': [INACTIVE_PERIOD_IN_DAYS],
        'wednesday': [INACTIVE_PERIOD_IN_DAYS],
        'thursday': [INACTIVE_PERIOD_IN_DAYS],
        'friday': [INACTIVE_PERIOD_IN_DAYS],
        'saturday': [INACTIVE_PERIOD_IN_DAYS],
        'sunday': [INACTIVE_PERIOD_IN_DAYS]
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

        clients = []
        for client_id in clients_id:
            last_order = Order.query(Order.client_id == client_id).order(-Order.date_created).get()
            if last_order.date_created > datetime.now() - timedelta(days=self.INACTIVE_PERIOD_IN_DAYS - 1):
                clients_id.remove(client_id)
            else:
                client = Client.get_by_id(client_id)
                client.last_order_date = last_order.date_created
                clients.append(client)

        html_file = jinja2.get_jinja2(app=self.app).render_template(
            'inactive_clients_period.html', clients=clients)

        email.send_error('analytics', u'Люди без заказов в течении 3-х недель', body="",  html=html_file)

        #for client_id in clients_id:
            #client = Client.get_by_id(client_id)
            #score = empatika_promos.get_user_points(client.key.id()) % 5
            #name = client.name if client.name_confirmed else None
            #send_reminder_push(client_id, name, score)
            #notification = Notification(client_id=client_id, type=PUSH_NOTIFICATION)
            #notification.put()