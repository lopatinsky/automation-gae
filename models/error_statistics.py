__author__ = 'dvpermyakov'

from google.appengine.ext import ndb


class AlfaBankRequest(ndb.Model):
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    url = ndb.StringProperty(required=True, indexed=False)
    success = ndb.BooleanProperty(required=True, indexed=False)
    error_code = ndb.IntegerProperty(required=True, indexed=False)
    error_message = ndb.StringProperty(indexed=False)


class PaymentErrorsStatistics(ndb.Model):
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    alfa_bank_requests = ndb.StructuredProperty(AlfaBankRequest, repeated=True)

    @classmethod
    def append_request(cls, **kwargs):
        statistics = cls.query().order(-cls.data_created).get()
        if not statistics or len(statistics.alfa_bank_requests) >= 1000:
            statistics = cls()
        statistics.alfa_bank_requests.append(AlfaBankRequest(**kwargs))
        statistics.put()

    @classmethod
    def get_requests(cls, since):
        statistics = cls.query(cls.data_created >= since).fetch()
        prev_statistics = cls.query(cls.data_created < since).order(- cls.data_created).get()

        requests = []
        if prev_statistics:
            for r in prev_statistics.alfa_bank_requests:
                if r.data_created >= since:
                    requests.append(r)
        for s in statistics:
            requests += s.alfa_bank_requests
        return requests
