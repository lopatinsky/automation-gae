# coding:utf-8
import logging
from webapp2 import cached_property
from handlers.api.user.base import UserApiHandler
from models import AdminStatus


class AdminApiHandler(UserApiHandler):
    @cached_property
    def _is_android_barista_app(self):
        return self.request.user_agent.startswith("Dalvik/")

    @cached_property
    def _token_entity(self):
        full_token = self.request.get("token")
        if full_token:
            uid, token = full_token.split("_", 1)
            return AdminStatus.get(uid, token)
        return None

    def send_error(self, description):
        self.response.set_status(400)
        logging.warning(description)
        self.render_json({
            'success': False,
            'description': description
        })

    @property
    def venue_or_error(self):
        return self.user.venue_entity
