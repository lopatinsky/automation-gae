# coding=utf-8
import logging
from google.appengine.api import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2_extras import auth
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from methods.auth import set_current_user

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
        #namespace = latinize(login)
        error = None
        #for metadata_instance in metadata.get_namespaces():
        #    if namespace == metadata_instance:
        #        error = u"Введите другой email"
        if error:
            pass
        elif not login:
            error = u"Не введен email"
        elif not password:
            error = u"Не введен пароль"
        elif password != password2:
            error = u"Пароли не совпадают"
        else:
            success, user = CompanyUser.create_user(login, login=login, password_raw=password)
            if not success:
                error = u"Пользователь с этим email уже зарегистрирован"
            else:
                #namespace_manager.set_namespace(user.namespace)
                #success, user = CompanyUser.create_user(id=user.key.id(), auth_id=login, namespace=namespace,
                #                                        login=login, password_raw=password, fucking_password=password)
                #if success:
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
        email, password = self.request.POST.get("login").lower().strip(), \
            self.request.POST.get("password")
        try:
            logging.info(email)
            logging.info(password)
            self.auth.get_user_by_password(email, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.render('/login.html', email=email,
                        error=u"Неверный логин или пароль")
        else:
            self.success()


class LogoutHandler(CompanyBaseHandler):
    def get(self):
        self.auth.unset_session()
        self.redirect('/company/login')