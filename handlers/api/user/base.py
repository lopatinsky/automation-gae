# coding:utf-8
import logging
from webapp2 import cached_property
from webapp2_extras import auth
from handlers.api.base import ApiHandler
from google.appengine.api.namespace_manager import namespace_manager
from models.user import UserStatus


class UserApiHandler(ApiHandler):
    def dispatch(self):
        if self.user:
            logging.info(self.user)
            namespace_manager.set_namespace(self.user.namespace)
        else:
            namespace_manager.set_namespace('')
        logging.debug('namespace=%s' % namespace_manager.get_namespace())
        super(UserApiHandler, self).dispatch()

    @cached_property
    def _token_entity(self):
        full_token = self.request.get("token")
        if full_token:
            uid, token = full_token.split("_", 1)
            return UserStatus.get(uid, token)
        return None

    @cached_property
    def auth(self):
        return auth.get_auth(request=self.request)

    @cached_property
    def _user_and_token(self):
        if self._token_entity:
            return self._token_entity.user, self._token_entity.token
        return None, None

    @cached_property
    def user(self):
        return self._user_and_token[0]

    @cached_property
    def token(self):
        return self._user_and_token[1]