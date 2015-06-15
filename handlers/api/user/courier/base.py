from webapp2 import cached_property
from handlers.api.user.base import UserApiHandler
from models.user import CourierStatus

__author__ = 'dvpermyakov'


class CourierBaseHandler(UserApiHandler):
    @cached_property
    def _token_entity(self):
        full_token = self.request.get("token")
        if full_token:
            uid, token = full_token.split("_", 1)
            return CourierStatus.get(uid, token)
        return None