__author__ = 'dvpermyakov'

from models import Client, CardBindingPayment, Notification, SMS_PASSIVE
from report_methods import suitable_date, PROJECT_STARTING_YEAR
from datetime import datetime
from config import config
import logging


def get(chosen_year, chosen_month, chosen_days, chosen_type, client_id):

    ALL = 0
    SUCCESS = 1
    CANCELLED = 2
    WITHOUT_TRY = 3
    ERRORS = 4

    if not chosen_year:
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_days = [datetime.now().day]
        chosen_type = ALL
    else:
        chosen_year = int(chosen_year)

    chosen_days = [int(day) for day in chosen_days]
    min_day = min(chosen_days)
    max_day = max(chosen_days)
    start = suitable_date(min_day, chosen_month, chosen_year, True)
    end = suitable_date(max_day, chosen_month, chosen_year, False)
    clients = Client.query(Client.created > start, Client.created < end).fetch()

    if client_id:
        if client_id.isdigit():
            client_id = int(client_id)
            client = Client.get_by_id(client_id)
        else:
            client = None
        if not client:
            clients = []
        else:
            clients = [client]

    for client in clients:
        client.created += config.TIMEZONE_OFFSET
        sms = Notification.query(Notification.client_id == client.key.id(), Notification.type == SMS_PASSIVE).get()
        if sms:
            client.sms_date = sms.created + config.TIMEZONE_OFFSET
        else:
            client.sms_date = None
        client.attempts = CardBindingPayment.query(CardBindingPayment.client_id == client.key.id()).fetch()
        client.web_failures = 0
        client.card_errors = []
        for attempt in client.attempts:
            if attempt.success is None:
                client.web_failures += 1
            elif not attempt.success:
                client.card_errors.append(attempt.error) if hasattr(attempt, 'error') else None
            elif attempt.success:
                client.card_end_date = attempt.updated + config.TIMEZONE_OFFSET
                client.card_start_date = attempt.created + config.TIMEZONE_OFFSET

    clients_with_card = []
    passive_clients = []
    cancelled_clients = []
    error_clients = []
    for client in clients:
        if client.tied_card:
            clients_with_card.append(client)
        elif len(client.card_errors):
            error_clients.append(client)
        elif client.web_failures:
            cancelled_clients.append(client)
        else:
            passive_clients.append(client)

    if chosen_type == SUCCESS:
        clients = clients_with_card
    elif chosen_type == CANCELLED:
        clients = cancelled_clients
    elif chosen_type == WITHOUT_TRY:
        clients = passive_clients
    elif chosen_type == ERRORS:
        clients = error_clients

    total = dict()
    total['sms'] = len([client for client in clients if client.sms_date])
    total['attempts'] = sum(len(client.attempts) for client in clients)
    total['web_failures'] = sum(client.web_failures for client in clients)
    total['card_errors'] = sum(len(client.card_errors)for client in clients)
    total['tied_card'] = sum(client.tied_card for client in clients)

    return {
        'clients': clients,
        'total': total,
        'start_year': PROJECT_STARTING_YEAR,
        'end_year': datetime.now().year,
        'chosen_year': chosen_year,
        'chosen_month': chosen_month,
        'chosen_days': chosen_days,
        'chosen_type': chosen_type,
        'all': ALL,
        'success': SUCCESS,
        'cancelled': CANCELLED,
        'without_try': WITHOUT_TRY,
        'errors': ERRORS
    }