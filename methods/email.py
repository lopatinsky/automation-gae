from google.appengine.api import app_identity, mail
from config import config

_EMAIL_DOMAIN = "%s.appspotmail.com" % app_identity.get_application_id()


def send_error(scope, subject, body):
    subject = "[DoubleB] " + subject
    if config.DEBUG:
        subject = "[Test]" + subject
    sender = "%s_errors@%s" % (scope, _EMAIL_DOMAIN)
    recipients = config.EMAILS.get(scope, "mdburshteyn@gmail.com")
    if recipients == "admins":
        mail.send_mail_to_admins(sender, subject, body)
    else:
        try:
            mail.send_mail(sender, recipients, subject, body)
        except:
            pass
