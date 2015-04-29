# coding=utf-8
import logging
from google.appengine.api import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2_extras import auth
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from methods.auth import set_current_user, company_user_required

__author__ = 'dvpermyakov'

from base import CompanyBaseHandler
from models import CompanyUser
from methods.rendering import latinize


class SignupHandler(CompanyBaseHandler):
    def success(self):
        self.redirect("/company/main")

    def get(self):
        if self.user is not None:
            self.success()
        else:
            self.render('/signup.html')

    def post(self):
        if self.user is not None:
            self.success()
        login, password, password2 = \
            self.request.get("email").strip().lower(), \
            self.request.get("password"), self.request.get("password2")
        namespace = latinize(login)
        error = None
        for metadata_instance in metadata.get_namespaces():
            if namespace == metadata_instance:
                error = u"Введите другой email"
        if error:
            pass
        elif not login:
            error = u"Не введен email"
        elif not password:
            error = u"Не введен пароль"
        elif password != password2:
            error = u"Пароли не совпадают"
        else:
            values = {
                'namespace': namespace,
                'login': login,
                'password_raw': password
            }
            success, user = CompanyUser.create_user(login, **values)
            if not success:
                error = u"Пользователь с этим email уже зарегистрирован"
            else:
                set_current_user(self.auth, user)
        if error:
            logging.info(error)
            self.render('/signup.html', email=login, error=error)
        else:
            self.success()


class LoginHandler(CompanyBaseHandler):
    def success(self):
        self.redirect('/company/main')

    def get(self):
        if self.user is not None:
            self.success()
        else:
            self.render('/login.html')

    def post(self):
        if self.user is not None:
            self.success()
        login = self.request.POST.get("login").lower().strip()
        password = self.request.POST.get("password")
        try:
            self.auth.get_user_by_password(login, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.render('/login.html', login=login, error=u"Неверный логин или пароль")
        else:
            self.success()


@company_user_required
class LogoutHandler(CompanyBaseHandler):
    def get(self):
        self.auth.unset_session()
        self.redirect('/company/login')