import datetime
import logging
from webapp2 import RequestHandler
from methods import email
from models import AdminStatus


class CheckPingsHandler(RequestHandler):
    def get(self):
        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(minutes=10)
        statuses = AdminStatus.query(AdminStatus.time < now - delta).fetch()
        if not statuses:
            return  # all pings up-to-date
        status_template = "Token: %s\n" \
                          "Last ping time: %s\n" \
                          "Login: %s"
        statuses_text = "\n\n".join(status_template % (status.key.id(), status.time, status.admin.email)
                                    for status in statuses)
        body = "Error: no ping in last 10 minutes\n" \
               "Current server time: %s\n\n" \
               "%s" % (now, statuses_text)
        logging.error(body)
        email.send_error("ping_errors", "Ping error", body)
