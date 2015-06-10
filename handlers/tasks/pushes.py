from handlers.web_admin.web.company import CompanyBaseHandler
from models import Notification
from models.specials import STATUS_CREATED
from methods.push import send_push, make_push_data
from models.client import IOS_DEVICE, ANDROID_DEVICE

__author__ = 'dvpermyakov'


class StartPushesHandler(CompanyBaseHandler):
    def post(self):
        notification_id = self.request.get_range('notification_id')
        notification = Notification.get_by_id(notification_id)
        if not notification:
            self.abort(400)
        if notification.status == STATUS_CREATED:
            channels = []
            for channel in notification.channels:
                channels.append(channel.channel)
            data = make_push_data(notification.text, notification.header, ANDROID_DEVICE)
            send_push(channels, data, ANDROID_DEVICE)

            data = make_push_data(notification.text, notification.header, IOS_DEVICE)
            send_push(channels, data, IOS_DEVICE)

            notification.closed()