__author__ = 'dvpermyakov'

from models import Client, Order, CardBindingPayment
from report_methods import suitable_date, PROJECT_STARTING_YEAR
from datetime import datetime


def get(chosen_year, chosen_month, chosen_day):
    if not chosen_year:
        chosen_year = datetime.now().year
        chosen_month = datetime.now().month
        chosen_day = datetime.now().day
    else:
        chosen_year = int(chosen_year)
    start = suitable_date(chosen_day, chosen_month, chosen_year, True)
    end = suitable_date(chosen_day, chosen_month, chosen_year, False)
    clients = Client.query(Client.created > start, Client.created < end).fetch()
    for client in clients[:]:
        order = Order.query(Order.client_id == client.key.id()).get()
        if order:
            clients.remove(client)
    for client in clients:
        client.attempts = CardBindingPayment.query(CardBindingPayment.client_id == client.key.id()).fetch()
        client.web_failures = 0
        client.card_errors = []
        for attempt in client.attempts:
            if attempt.success is None:
                client.web_failures += 1
            elif not attempt.success:
                client.card_errors.append(attempt.error) if hasattr(attempt, 'error') else None

    total = dict()
    total['clients_number'] = len(clients)
    total['clients_success'] = sum(len(client.attempts) == 1 and client.tied_card for client in clients)

    clients = [client for client in clients if client.attempts]
    clients = [client for client in clients if not (len(client.attempts) == 1 and client.tied_card)]

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
        'chosen_day': chosen_day
    }