import datetime
from webapp2 import RequestHandler
from methods import email
from models import SharedGift

MAX_DAYS_BEFORE_CANCEL = 7


class CancelGiftsHandler(RequestHandler):
    def get(self):
        time = datetime.datetime.now() - datetime.timedelta(days=MAX_DAYS_BEFORE_CANCEL)
        unused_gifts = SharedGift.query(SharedGift.status == SharedGift.READY)
        old_gifts = [g for g in unused_gifts if g.created < time]
        if old_gifts:
            email.send_error("order", "Unused gifts found", "Gifts not used within 7 days: %s" % len(old_gifts))
            for gift in old_gifts:
                gift.cancel()