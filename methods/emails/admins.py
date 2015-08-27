from google.appengine.api import app_identity, mail, namespace_manager

_EMAIL_DOMAIN = "%s.appspotmail.com" % app_identity.get_application_id()


def send_error(scope, subject, body, html=None):
    namespace = namespace_manager.get_namespace()
    subject = "[Auto][%s] " % namespace + subject
    sender = "%s_errors@%s" % (scope, _EMAIL_DOMAIN)
    kw = {'html': html} if html else {}
    mail.send_mail_to_admins(sender, subject, body, **kw)
