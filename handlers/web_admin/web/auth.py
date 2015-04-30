# coding=utf-8
from google.appengine.api import namespace_manager
from webapp2 import cached_property

from .base import BaseHandler
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from methods.auth import set_current_user, user_required
from models import Venue, Admin
import logging


class LoginHandler(BaseHandler):
    def success(self):
        self.redirect("orders")

    def get(self):
        if self.user is not None:
            self.success()
        else:
            self.render('login.html')

    def post(self):
        if self.user is not None:
            self.success()
        email, password = self.request.POST.get("email").lower().strip(), \
            self.request.POST.get("password")
        try:
            self.auth.get_user_by_password(email, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.render('login.html', email=email,
                        error=u"Неверный логин или пароль")
        else:
            self.success()


class LogoutHandler(BaseHandler):
    @user_required
    def get(self):
        self.auth.unset_session()
        self.redirect("login")
