from google.appengine.api import app_identity, mail, namespace_manager
from config import config

_EMAIL_DOMAIN = "%s.appspotmail.com" % app_identity.get_application_id()


def send_error(scope, subject, body, html=None):
    namespace = namespace_manager.get_namespace()
    subject = "[Auto][%s] " % namespace + subject
    sender = "%s_errors@%s" % (scope, _EMAIL_DOMAIN)
    recipients = config.EMAILS.get(scope, "mdburshteyn@gmail.com")
    kw = {'html': html} if html else {}
    if recipients == "admins":
        mail.send_mail_to_admins(sender, subject, body, **kw)
    else:
        try:
            mail.send_mail(sender, recipients, subject, body, **kw)
        except:
            pass
