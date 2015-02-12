# coding=utf-8

from ..base import BaseHandler
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from methods import auth
from models import Admin


class LoginHandler(BaseHandler):
    def success(self):
        self.redirect_to('padmin_report')

    def get(self):
        if self.user is not None:
            self.success()
        else:
            self.render('/mt/private_office/login.html')

    def post(self):
        if self.user is not None:
            self.success()
        login = self.request.POST.get("login").lower().strip()
        password = self.request.POST.get("password")
        try:
            auth_id = '%s:%s' % (Admin.PADMIN, login)
            self.auth.get_user_by_password(auth_id, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.render('/mt/private_office/login.html', email=login, error=u"Неверный логин или пароль")
        else:
            self.success()


class LogoutHandler(BaseHandler):
    @auth.padmin_user_required
    def get(self):
        self.auth.unset_session()
        self.redirect_to('padmin_login')