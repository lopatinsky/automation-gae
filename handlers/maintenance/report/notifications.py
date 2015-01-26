__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import Order, Notification, SMS_NOTIFICATION, PUSH_NOTIFICATION
from datetime import datetime, timedelta
from report_methods import suitable_date, PROJECT_STARTING_YEAR
import calendar


class NotificationsReportHandler(BaseHandler):
    DAYS_AFTER_NOTIFICATION = 7

    def get(self):
        chosen_year = self.request.get("selected_year")
        chosen_month = self.request.get_range("selected_month")
        chosen_type = self.request.get_range("selected_type")
        if not chosen_year:
            chosen_year = datetime.now().year
            chosen_month = datetime.now().month
        else:
            chosen_year = int(chosen_year)

        pushes_info = []
        total = {
            'notification_new': 0,
            'notification_old': 0,
            'order_numbers': [0] * self.DAYS_AFTER_NOTIFICATION,
        }
        for day in range(1, calendar.monthrange(chosen_year, chosen_month)[1] + 1):
            date_begin = suitable_date(day, chosen_month, chosen_year, True)
            date_end = suitable_date(day, chosen_month, chosen_year, False)
            query = Notification.query(Notification.type == chosen_type)
            query = query.filter(Notification.created >= date_begin)
            query = query.filter(Notification.created <= date_end)
            notifications = query.fetch()
            notification_new = 0
            notification_old = 0
            order_numbers = [0] * self.DAYS_AFTER_NOTIFICATION
            for notification in notifications:
                client_id = notification.client_id
                first_notification = Notification.query(Notification.client_id == client_id).order(Notification.created).get()
                if notification.key.id() != first_notification.key.id():
                    notification_old += 1
                else:
                    notification_new += 1
                for index in xrange(self.DAYS_AFTER_NOTIFICATION):
                    curr_date_begin = date_begin + timedelta(days=index + 1)
                    curr_date_end = date_end + timedelta(days=index + 1)
                    order_number = Order.query(
                        Order.client_id == client_id, Order.date_created >= curr_date_begin,
                        Order.date_created <= curr_date_end).count()
                    order_numbers[index] = order_number
                    total['order_numbers'][index] += order_number

            pushes_info.append({
                'day': day,
                'notification_new': notification_new,
                'notification_old': notification_old,
                'order_numbers': order_numbers
            })
            total['notification_new'] = notification_new
            total['notification_old'] = notification_old
        values = {
            'notification_info': pushes_info,
            'start_year': PROJECT_STARTING_YEAR,
            'end_year': datetime.now().year,
            'chosen_year': chosen_year,
            'chosen_month': chosen_month,
            'chosen_type': chosen_type,
            'sms_type': SMS_NOTIFICATION,
            'push_type': PUSH_NOTIFICATION,
            'days_after_notification': self.DAYS_AFTER_NOTIFICATION,
            'total': total
        }
        self.render('reported_notification.html', **values)