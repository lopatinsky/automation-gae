# coding=utf-8
import datetime
from StringIO import StringIO
from google.appengine.api import namespace_manager, mail, app_identity
from google.appengine.ext import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from config import Config
from methods import excel
from methods.report import orders


_EMAIL_SENDER = "reports@%s.appspotmail.com" % app_identity.get_application_id()


def _send(namespace, emails):
    namespace_manager.set_namespace(namespace)
    config = Config.get()

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    report_data = orders.get('0', yesterday.year, yesterday.month, yesterday.day)

    excel_file = excel.send_excel_file(None, 'orders', 'orders.html', **report_data)
    io = StringIO()
    excel_file.save(io)

    subject = u"Отчет по продажам через мобильное приложение %s за %s" % \
              (config.APP_NAME, yesterday.strftime("%d.%m.%Y"))
    filename = u"report-%s-%s.xls" % (namespace, yesterday.strftime("%d-%m-%Y"))
    filename = filename.encode('utf-8')

    mail.send_mail(_EMAIL_SENDER, emails, subject, '', attachments=[mail.Attachment(filename, io.getvalue())])


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
