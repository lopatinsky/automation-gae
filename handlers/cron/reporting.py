# coding=utf-8
import datetime
from StringIO import StringIO

from google.appengine.api import namespace_manager, mail, app_identity
from google.appengine.ext import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from models.config.config import Config
from methods import excel
from methods.report import orders

_EMAIL_SENDER = "reports@%s.appspotmail.com" % app_identity.get_application_id()


def _send(namespace, emails):
    namespace_manager.set_namespace(namespace)
    config = Config.get()

    today = datetime.datetime.combine(datetime.date.today(), datetime.time())
    yesterday = today - datetime.timedelta(days=1)
    yesterday_end = today - datetime.timedelta(microseconds=1)
    report_data = orders.get('0', yesterday, yesterday_end)

    excel_file = excel.send_excel_file(None, 'orders', 'orders.html', **report_data)
    io = StringIO()
    excel_file.save(io)

    subject = u"Приложение %s - отчет" % config.APP_NAME
    body = u"Отчет за дату: %s" % yesterday.strftime("%d.%m.%Y")
    filename = u"report-%s-%s.xls" % (namespace, yesterday.strftime("%d-%m-%Y"))
    filename = filename.encode('utf-8')

    mail.send_mail(_EMAIL_SENDER, emails, subject, body, attachments=[mail.Attachment(filename, io.getvalue())])


class ReportSendHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            config = Config.get()
            if not config:
                continue
            if not config.REPORT_EMAILS:
                continue
            emails = config.REPORT_EMAILS.split(",")
            deferred.defer(_send, namespace, emails)
