from handlers.web_admin.web.company.base import CompanyBaseHandler
from models.config.share import ShareInvitationModule

__author__ = 'Artem'
from models.config import config


class SetInvitationModuleHandler(CompanyBaseHandler):
    def get(self):
        # self.response.write('hello')
        conf = config.Config.get()
        if not conf.SHARE_INVITATION_MODULE:
            conf.SHARE_INVITATION_MODULE = ShareInvitationModule()
            conf.SHARE_INVITATION_MODULE.status = 0
        self.render('/config_settings/invitation_module_setup.html')

    def post(self):
        status = self.request.get('status') is not ''
        # status = self.request.get_range('status', min_value=0, max_value=1, default=1)
        after_order = self.request.get('after_order') is not ''
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

        if not conf.SHARE_INVITATION_MODULE:
            conf.SHARE_INVITATION_MODULE = ShareInvitationModule()

        share_invitation_module = conf.SHARE_INVITATION_MODULE

        share_invitation_module.status = status
        share_invitation_module.after_order = after_order
        share_invitation_module.after_number_order = after_number_order
        share_invitation_module.about_title = about_title
        share_invitation_module.about_description = about_description
        share_invitation_module.invitation_text = invitation_text
        share_invitation_module.invitation_image = invitation_image
        share_invitation_module.sender_accumulated_points = sender_accumulated_points
        share_invitation_module.sender_wallet_points = sender_wallet_points
        share_invitation_module.recipient_accumulated_points = recipient_accumulated_points
        share_invitation_module.recipient_wallet_points = recipient_wallet_points

        conf.put()

        self.redirect_to('company_main')


class CreateBrachApiKey(CompanyBaseHandler):
    def get(self):
        
        pass

    def post(self):
        pass