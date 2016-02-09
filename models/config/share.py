from google.appengine.ext import ndb

from methods.fuckups import is_share_fuckup_ios_user
from models import STATUS_CHOICES, STATUS_AVAILABLE
from models.config.config import SHARE_GIFT, SHARE_INVITATION

__author__ = 'dvpermyakov'


class ShareInvitationModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    after_order = ndb.BooleanProperty(default=True)
    after_number_order = ndb.IntegerProperty(default=3)  # can't be zero

    about_title = ndb.StringProperty(required=True)
    about_description = ndb.StringProperty(required=True)
    invitation_text = ndb.StringProperty(required=True)
    invitation_image = ndb.StringProperty()

    sender_accumulated_points = ndb.IntegerProperty(default=0)
    sender_wallet_points = ndb.IntegerProperty(default=0)
    recipient_accumulated_points = ndb.IntegerProperty(default=0)
    recipient_wallet_points = ndb.IntegerProperty(default=0)

    @classmethod
    def has_module(cls, config):
        module_enable = config.SHARE_INVITATION_MODULE is not None and \
            config.SHARE_INVITATION_MODULE.status == STATUS_AVAILABLE and \
            config.BRANCH_API_KEY is not None and \
            config.BRANCH_SECRET_KEY is not None
        if is_share_fuckup_ios_user():
            module_enable = False
        return module_enable

    def dict(self):
        return {
            'type': SHARE_INVITATION,
            'info': {
                'about': {
                    'title': self.about_title,
                    'description': self.about_description
                }
            }
        }


class ShareGiftModule(ndb.Model):
    status = ndb.IntegerProperty(choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    @classmethod
    def has_module(cls):
        from models.config.config import config
        return config.SHARE_GIFT_MODULE.status == STATUS_AVAILABLE \
            if config.SHARE_GIFT_MODULE \
            and config.BRANCH_API_KEY and config.BRANCH_SECRET_KEY \
            else False

    def dict(self):
        return {
            'type': SHARE_GIFT
        }
