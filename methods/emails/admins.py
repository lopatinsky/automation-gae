from google.appengine.api import mail, namespace_manager
from models.config.version import CURRENT_APP_ID

_EMAIL_DOMAIN = "%s.appspotmail.com" % CURRENT_APP_ID


def send_error(scope, subject, body, html=None):
    namespace = namespace_manager.get_namespace()
    subject = "[Auto][%s] " % namespace + subject
    sender = "%s_errors@%s" % (scope, _EMAIL_DOMAIN)
    kw = {'html': html} if html else {}
    mail.send_mail_to_admins(sender, subject, body, **kw)
