import datetime
import logging
from google.appengine.api import mail
from google.appengine.api.app_identity import app_identity
from webapp2 import RequestHandler
from models import AdminStatus

_EMAIL_SENDER = "ping_errors@%s.appspotmail.com" % app_identity.get_application_id()


class CheckPingsHandler(RequestHandler):
    def get(self):
        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(minutes=10)
        statuses = AdminStatus.query(AdminStatus.time < now - delta).fetch()
        if not statuses:
            return  # all pings up-to-date
        status_template = "Token: %s\n" \
                          "Last ping time: %s\n" \
                          "Email: %s"
        statuses_text = "\n\n".join(status_template % (status.key.id(), status.time, status.admin.email)
                                    for status in statuses)
        body = "Error: no ping in last 10 minutes\n" \
               "Current server time: %s\n\n" \
               "%s" % (now, statuses_text)
        logging.error(body)
        try:
            mail.send_mail(_EMAIL_SENDER, "mdburshteyn@gmail.com", "[DoubleB] Ping error", body)  # TODO recipient
        except:
            pass
