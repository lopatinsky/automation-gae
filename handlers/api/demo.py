# coding=utf-8
from urlparse import urlparse

from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError

from handlers.api.base import ApiHandler
from models import CompanyUser
from models.config.version import DEMO_HOSTNAME

__author__ = 'dvpermyakov'


class DemoLoginHandler(ApiHandler):
    def render_error(self, description):
        self.render_json({
            'success': False,
            'description': description
        })

    def post(self):
        if urlparse(self.request.url).hostname != DEMO_HOSTNAME:
            self.abort(403)
        login = self.request.get('login')
        password = self.request.get('password')
        try:
            user_dict = self.auth.get_user_by_password(login, password, save_session=False)
            user = CompanyUser.get_by_id(user_dict.get('user_id'))
            if not user:
                return self.render_error(u'Не найден пользователь')
            if not user.namespace:
                return self.render_error(u'Не найдено пространство имен')
            self.render_json({
                'success': True,
                'namespace': user.namespace
            })
        except (InvalidAuthIdError, InvalidPasswordError):
            return self.render_error(u'Неверные имя или пароль')