from datetime import datetime
from webapp2 import RequestHandler
from models import Notification
from models.specials import STATUS_CREATED, ReviewPush
from methods.push import send_multichannel_push, send_review_push
from models.client import IOS_DEVICE, ANDROID_DEVICE

__author__ = 'dvpermyakov'


class StartPushesHandler(RequestHandler):
    def post(self):
        notification_id = self.request.get_range('notification_id')
        notification = Notification.get_by_id(notification_id)
        if not notification:
            self.abort(400)
        if notification.status == STATUS_CREATED:
            channels = []
            for channel in notification.channels:
                channels.append(channel.channel)
            send_multichannel_push(notification.text, notification.header, channels, ANDROID_DEVICE)
            send_multichannel_push(notification.text, notification.header, channels, IOS_DEVICE)

            notification.closed()


class SendPushReviewHandler(RequestHandler):
    def post(self):
        review_id = self.request.get_range('review_id')
        review = ReviewPush.get_by_id(review_id)
        if not review:
            self.abort(400)
        order = review.order.get()
        send_review_push(order)
        review.sent = datetime.utcnow()
        review.put()
