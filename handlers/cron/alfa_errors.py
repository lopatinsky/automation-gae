import datetime
from webapp2 import RequestHandler
from methods import email
from models.error_statistics import PaymentErrorsStatistics


class CheckAlfaErrorsHandler(RequestHandler):
    def get(self):
        now = datetime.datetime.now()
        since = now - datetime.timedelta(minutes=10)
        requests = PaymentErrorsStatistics.get_requests(since)
        if not requests:
            return
        failure_count = sum(int(not r.success) for r in requests)
        if float(failure_count) / len(requests) > 0.2:
            email.send_error("server", "Payment errors", "Last 10 minutes: %s errors out of %s requests" %
                             (failure_count, len(requests)))
