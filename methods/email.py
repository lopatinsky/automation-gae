from google.appengine.api import app_identity, mail

_EMAIL_DOMAIN = "%s.appspotmail.com" % app_identity.get_application_id()


def send_error(sender, subject, body):
    subject = "[DoubleB] " + subject
    # mail.send_mail_to_admins("%s@%s" % (sender, _EMAIL_DOMAIN), subject, body)  # TODO send to all
    try:
        mail.send_mail("%s@%s" % (sender, _EMAIL_DOMAIN), "mdburshteyn@gmail.com", subject, body)
    except:
        pass
