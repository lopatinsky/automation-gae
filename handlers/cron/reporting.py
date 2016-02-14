# coding=utf-8
import datetime
from StringIO import StringIO

from google.appengine.api import namespace_manager, mail
from google.appengine.ext import deferred
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from methods.rendering import latinize

from models.config.config import config, COMPANY_IN_PRODUCTION
from methods import excel
from methods.report import orders
from models.config.version import CURRENT_APP_ID
from models.legal import LegalInfo

_EMAIL_SENDER = "reports@%s.appspotmail.com" % CURRENT_APP_ID


def _send(namespace):
    namespace_manager.set_namespace(namespace)
    company_emails = config.REPORT_EMAILS.split(",") if config.REPORT_EMAILS else ()

    today = datetime.datetime.combine(datetime.date.today(), datetime.time())
    yesterday = today - datetime.timedelta(days=1)
    yesterday_end = today - datetime.timedelta(microseconds=1)

    all_reports = []

    legals = LegalInfo.query().fetch()
    for legal in legals:
        legal_emails = legal.report_emails.split(",") if legal.report_emails else ()
        if not legal_emails and not company_emails:
            continue
        venue_ids = legal.get_venue_ids()
        if not venue_ids:
            continue

        report_data = orders.get(None, yesterday, yesterday_end, venue_ids=legal.get_venue_ids())
        excel_file = excel.send_excel_file(None, 'orders', 'orders.html', **report_data)
        io = StringIO()
        excel_file.save(io)

        legal_name = legal.person_ooo or legal.person_ip
        filename = u"report-%s-%s-%s.xls" % (namespace, latinize(legal_name), yesterday.strftime("%d-%m-%Y"))
        filename = filename.encode('utf-8')
        attachment = mail.Attachment(filename, io.getvalue())
        all_reports.append(attachment)

        if legal_emails:
            subject = u"Приложение %s - отчет для %s" % (config.APP_NAME, legal_name)
            body = u"Отчет за дату: %s" % yesterday.strftime("%d.%m.%Y")
            mail.send_mail(_EMAIL_SENDER, legal_emails, subject, body, attachments=[attachment])

    if company_emails and all_reports:
        subject = u"Приложение %s - отчет" % config.APP_NAME
        body = u"Отчет за дату: %s" % yesterday.strftime("%d.%m.%Y")
        mail.send_mail(_EMAIL_SENDER, company_emails, subject, body, attachments=all_reports)


class ReportSendHandler(RequestHandler):
    def get(self):
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            if not config or config.COMPANY_STATUS != COMPANY_IN_PRODUCTION:
                continue
            deferred.defer(_send, namespace)
