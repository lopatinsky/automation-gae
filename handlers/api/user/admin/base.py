# coding:utf-8
from webapp2 import cached_property
from handlers.api.user.base import UserApiHandler
from models import AdminStatus


class AdminApiHandler(UserApiHandler):
    @cached_property
    def _token_entity(self):
        full_token = self.request.get("token")
        if full_token:
            uid, token = full_token.split("_", 1)
            return AdminStatus.get(uid, token)
        return None

    def send_error(self, description):
        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': description
        })

    @property
    def venue_or_error(self):
        venue = None
        if self.user.venue:
            venue = self.user.venue.get()
        if not venue:
            return self.send_error(u'Не связки с точкой кофейни')
        return venue