from collections import defaultdict, Counter
import datetime
import logging

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from methods.emails import admins
from models.error_statistics import PaymentErrorsStatistics

MINUTES_INTERVAL = 10
AVAIL_FAILURE_PERCENT = 20


class CheckAlfaErrorsHandler(RequestHandler):
    def get(self):
        now = datetime.datetime.now()
        since = now - datetime.timedelta(minutes=MINUTES_INTERVAL)
        namespace_errors = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            requests = PaymentErrorsStatistics.get_requests(since)
            if requests:
                logging.info('-----------------------------')
                failure_count = sum(int(not r.success) for r in requests)
                if float(failure_count) / len(requests) > AVAIL_FAILURE_PERCENT / 100.0:
                    failure_info = defaultdict(Counter)  # url -> {message -> count}
                    for request in requests:
                        if not request.success:
                            failure_info[request.url][request.error_message] += 1
                    error_details = []
                    for url, messages in failure_info.iteritems():
                        messages_string = "\n".join("| %s: %s" % item for item in messages.items())
                        error_details.append("%s\n%s" % (url, messages_string))
                    text = u"%s errors out of %s requests\n\n%s" % (failure_count, len(requests), "\n\n".join(error_details))
                    namespace_errors[namespace] = text
        mail_body = u'Errors with AlfaBank within %s minutes and with %s%% of failures:\n' % \
                    (MINUTES_INTERVAL, AVAIL_FAILURE_PERCENT)
        for namespace in namespace_errors.keys():
            mail_body += u'In namespace = %s:\n' % namespace
            mail_body += namespace_errors[namespace]
        if namespace_errors:
            logging.warning(mail_body)
            admins.send_error("server", "Payment errors", mail_body)
