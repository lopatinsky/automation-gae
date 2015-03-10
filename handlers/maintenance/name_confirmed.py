# -*- coding: utf-8 -*-

__author__ = 'dvpermyakov'

from base import BaseHandler
from models import Client
from datetime import datetime
from methods.report.report_methods import suitable_date, PROJECT_STARTING_YEAR


class NameConfirmationHandler(BaseHandler):
    def get(self):
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            chosen_year = int(chosen_year)
        query = Client.query(Client.created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Client.created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
        clients = query.fetch()
        values = {
            'clients': clients,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day,
            'status': 'Click the button in the bottom to save'
        }
        self.render('name_confirmation.html', **values)

    def post(self):
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_day = self.request.get_range("selected_day")
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
            chosen_day = datetime.now().day
        else:
            chosen_year = int(chosen_year)
        query = Client.query(Client.created >= suitable_date(chosen_day, chosen_month, chosen_year, True))
        query = query.filter(Client.created <= suitable_date(chosen_day, chosen_month, chosen_year, False))
        clients = query.fetch()
        for client in clients:
            confirmed = bool(self.request.get(str(client.key.id())))
            client.name_confirmed = confirmed
            sms_name = self.request.get('name_for_sms_%s' % client.key.id())
            if confirmed:
                sms_name = client.name
            client.name_for_sms = sms_name
            client.put()
        values = {
            'clients': clients,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_day': chosen_day,
            'status': 'Saved!'
        }
        self.render('name_confirmation.html', **values)