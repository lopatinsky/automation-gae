from datetime import datetime, timedelta
import logging
from google.appengine.ext import ndb
from google.appengine.ext.deferred import deferred
from google.appengine.runtime import DeadlineExceededError
from webapp2 import RequestHandler
from models import TabletRequest


def _do():
    try:
        week_ago = datetime.now() - timedelta(days=7)
        query = TabletRequest.query(TabletRequest.request_time < week_ago)
        total_deleted = 0
        while True:
            keys = query.fetch(1000, keys_only=True)
            if not keys:
                break
            ndb.delete_multi(keys)
            total_deleted += len(keys)
            logging.info("total deleted: %s" % total_deleted)
    except DeadlineExceededError as e:
        deferred.defer(_do)
        logging.exception(e)


class ClearPingsHandler(RequestHandler):
    def get(self):
        deferred.defer(_do)
