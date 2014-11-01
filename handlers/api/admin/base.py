from webapp2 import cached_property
from webapp2_extras import auth
from ..base import ApiHandler


class AdminApiHandler(ApiHandler):
    @cached_property
    def auth(self):
        return auth.get_auth(request=self.request)

    @cached_property
    def _user_and_token(self):
        full_token = self.request.get("token")
        if full_token:
            uid, token = full_token.split("_", 1)
            if self.auth.get_user_by_token(int(uid), token, save_session=False):
                return self.auth.store.user_model.get_by_id(int(uid)), token
        return None, None

    @cached_property
    def user(self):
        return self._user_and_token[0]

    @cached_property
    def token(self):
        return self._user_and_token[1]
