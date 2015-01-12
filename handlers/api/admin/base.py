from webapp2 import cached_property
from webapp2_extras import auth
from ..base import ApiHandler
from models import AdminStatus


class AdminApiHandler(ApiHandler):
    @cached_property
    def _token_entity(self):
        full_token = self.request.get("token")
        if full_token:
            uid, token = full_token.split("_", 1)
            return AdminStatus.get(uid, token)
        return None

    @cached_property
    def auth(self):
        return auth.get_auth(request=self.request)

    @cached_property
    def _user_and_token(self):
        if self._token_entity:
            return self._token_entity.admin, self._token_entity.token
        return None, None

    @cached_property
    def user(self):
        return self._user_and_token[0]

    @cached_property
    def token(self):
        return self._user_and_token[1]
