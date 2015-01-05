import datetime
import logging
from webapp2 import RequestHandler
from methods import email
from models import AdminStatus, TabletRequest, Admin


AVAILABLE_BATTERY_LEVEL = 15
AVAILABLE_SOUND_LEVEL = 0


class CheckPingsHandler(RequestHandler):
    def get(self):
        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(minutes=10)
        statuses = AdminStatus.query(AdminStatus.time < now - delta).fetch()

        body_error = ""

        if statuses:
            status_template = "Token: %s\n" \
                              "Last ping time: %s\n" \
                              "Login: %s"
            statuses_text = "\n\n".join(status_template % (status.key.id(), status.time, status.admin.email)
                                        for status in statuses)
            body_error += "Error: no ping in last 10 minutes\n"\
                          "Current server time: %s\n\n" \
                          "%s" % (now, statuses_text)
            logging.error(body_error)

        admins = Admin.query().fetch()
        for admin in admins:
            info = ''
            requests = TabletRequest.query(TabletRequest.request_time > now - delta,
                                           TabletRequest.admin_id == admin.key.id()).fetch()
            is_turned_on = False
            is_low_sound = True
            is_low_battery = True
            for request in requests:
                if request.is_turned_on:
                    is_turned_on = True
                if request.is_in_charging or request.battery_level > AVAILABLE_BATTERY_LEVEL:
                    is_low_battery = False
                if not request.sound_level_system > AVAILABLE_SOUND_LEVEL:
                    is_low_sound = False
            if not is_turned_on:
                info += 'Tablet screen is turned off\n'
            if is_low_battery and is_turned_on:
                info += 'Tablet has low battery level\n'
            if is_low_sound and is_turned_on:
                info += 'Tablet has low sound level\n'

            if info:
                body_error += 'Id admin: %s\nErrors:\n%s\n\n' % (admin.email, info)
                logging.error(body_error)

        if body_error:
            email.send_error("ping", "Ping error", body_error)
