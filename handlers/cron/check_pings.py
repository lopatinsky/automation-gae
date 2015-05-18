import logging
from webapp2 import RequestHandler
from methods import email
from methods.pings import PingReport, LEVEL_OK, LEVEL_WARNING
from models import AdminStatus, Admin


_TEMPLATE = "Token: %s\n" \
    "Login: %s\n" \
    "%s"


class CheckPingsHandler(RequestHandler):
    def get(self):
        statuses = AdminStatus.query().fetch()

        reports = [PingReport(status) for status in statuses if status.admin.get_role() == Admin.ROLE]
        error_reports = [report for report in reports if report.error_level > LEVEL_OK]
        if not error_reports:
            return

        error_messages = [_TEMPLATE % (report.admin_status.key.id(), report.admin_status.admin.login,
                                       "\n".join(report.error_messages)) for report in error_reports]
        body = "\n\n".join(error_messages)

        logging.info(body)

        max_level = max(r.error_level for r in error_reports)
        subject = "Tablet monitoring " + ("warnings" if max_level == LEVEL_WARNING else "errors")
        #email.send_error("ping", subject, body)
