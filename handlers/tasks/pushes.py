from datetime import datetime

from webapp2 import RequestHandler

from methods.push import send_review_push
from models import Notification
# from models.push import *
from models.push import SimplePush
from models.specials import STATUS_CREATED, ReviewPush
from models.push import ReviewPush as RP
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

            android_push = SimplePush(text=notification.text, should_popup=notification.should_popup,
                                      full_text=notification.popup_text, header=notification.header,
                                      channels=channels, device_type=ANDROID_DEVICE)

            ios_push = SimplePush(text=notification.text, should_popup=notification.should_popup,
                                  full_text=notification.popup_text, header=notification.header,
                                  channels=channels, device_type=IOS_DEVICE)

            android_push.send()
            ios_push.send()

            notification.closed()


class SendPushReviewHandler(RequestHandler):
    def post(self):
        review_id = self.request.get_range('review_id')


        review = ReviewPush.get_by_id(review_id)
        if not review:
            self.abort(400)
        order = review.order.get()

        # push = ReviewPush(order, 0)
        # push.send()
        push = RP(order, 0)
        push.send()

        # send_review_push(order)
        review.sent = datetime.utcnow()
        review.put()
