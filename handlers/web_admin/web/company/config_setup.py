from handlers.web_admin.web.company.base import CompanyBaseHandler

__author__ = 'Artem'
from models.config import config


class SetInvitationModuleHandler(CompanyBaseHandler):
    def get(self):
        self.response.out.write('Hello')
        pass

    def post(self):
        status = self.request.get_range('status', min_value=0, max_value=1, default=1)
        after_order = self.request.get('after_order')
        after_number_order = self.request.get_range('after_number_order', min_value=1, default=3)

        about_title = self.request.get('about_title')
        about_description = self.request.get('about_description')
        invitation_text = self.request.get('invitation_text')
        invitation_image = self.request.get('invitation_image')

        sender_accumulated_points = self.request.get_range('sender_accumulated_points', default=0)
        sender_wallet_points = self.request.get_range('sender_wallet_points', default=0)

        recipient_accumulated_points = self.request.get_range('recipient_accumulated_points', default=0)
        recipient_wallet_points = self.request.get_range('recipient_wallet_points', default=0)

        conf = config.Config.get()

        conf.SHARE_INVITATION_MODULE.status = status
        conf.SHARE_INVITATION_MODULE.after_order = after_order
        conf.SHARE_INVITATION_MODULE.after_number_order = after_number_order
        conf.SHARE_INVITATION_MODULE.about_title = about_title
        conf.SHARE_INVITATION_MODULE.about_description = about_description
        conf.SHARE_INVITATION_MODULE.invitation_text = invitation_text
        conf.SHARE_INVITATION_MODULE.invitation_image = invitation_image
        conf.SHARE_INVITATION_MODULE.sender_accumulated_points = sender_accumulated_points
        conf.SHARE_INVITATION_MODULE.sender_wallet_points = sender_wallet_points
        conf.SHARE_INVITATION_MODULE.recipient_accumulated_points = recipient_accumulated_points
        conf.SHARE_INVITATION_MODULE.recipient_wallet_points = recipient_wallet_points

        conf.put()