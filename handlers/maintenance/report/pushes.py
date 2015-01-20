__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Client, Order
from datetime import datetime, timedelta
from report_methods import suitable_date, PROJECT_STARTING_YEAR
import calendar


class PushesReportHandler(BaseHandler):
    DAYS_AFTER_PUSH = 7

    def get(self):
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
        else:
            chosen_year = int(chosen_year)

        pushes_info = []
        total = {
            'push_new': 0,
            'push_old': 0,
            'order_numbers': [0] * self.DAYS_AFTER_PUSH,
        }
        for day in range(1, calendar.monthrange(chosen_year, chosen_month)[1] + 1):
            date_begin = suitable_date(day, chosen_month, chosen_year, True)
            date_end = suitable_date(day, chosen_month, chosen_year, False)
            query = Client.query(Client.created >= date_begin)
            query = query.filter(Client.created <= date_end)
            clients = query.fetch()
            push_new = 0
            push_old = 0
            order_numbers = [0] * self.DAYS_AFTER_PUSH
            for client in clients:
                if not client.push_numbers:
                    continue
                if client.push_numbers > 1:
                    push_old += 1
                else:
                    push_new += 1
                for index in xrange(self.DAYS_AFTER_PUSH):
                    curr_date_begin = date_begin + timedelta(days=index + 1)
                    curr_date_end = date_end + timedelta(days=index + 1)
                    order_number = Order.query(
                        Order.client_id == client.key.id(), Order.date_created >= curr_date_begin,
                        Order.date_created <= curr_date_end).count()
                    order_numbers[index] = order_number
                    total['order_numbers'][index] += order_number

            pushes_info.append({
                'day': day,
                'push_new': push_new,
                'push_old': push_old,
                'order_numbers': order_numbers
            })
            total['push_new'] = push_new
            total['push_old'] = push_old
        values = {
            'pushes_info': pushes_info,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'days_after_push': self.DAYS_AFTER_PUSH,
            'total': total
        }
        self.render('reported_pushes.html', **values)