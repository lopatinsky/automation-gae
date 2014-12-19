from collections import defaultdict, Counter
import datetime
import logging
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
            failure_info = defaultdict(Counter)  # url -> {message -> count}
            for request in requests:
                if not request.success:
                    failure_info[request.url][request.error_message] += 1

            error_details = []
            for url, messages in failure_info.iteritems():
                messages_string = "\n".join("| %s: %s" % item for item in messages.items())
                error_details.append("%s\n%s" % (url, messages_string))

            body = "Last 10 minutes: %s errors out of %s requests\n\n%s" % \
                   (failure_count, len(requests), "\n\n".join(error_details))

            logging.warning(body)

            email.send_error("server", "Payment errors", body)
