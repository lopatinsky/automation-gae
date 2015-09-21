# coding=utf-8
import logging

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError

from models.config.config import Config
from methods.auth import set_current_user

__author__ = 'dvpermyakov'

from base import CompanyBaseHandler
from models import CompanyUser, DeliverySlot
from methods.rendering import latinize


class CompanySignupHandler(CompanyBaseHandler):
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
            namespace_manager.set_namespace(namespace)
            cfg = Config(id=1)
            cfg.REPORT_EMAILS = 'elenamarchenko.lm@gmail.com'
            cfg.put()
            DeliverySlot(name=u'Сейчас', slot_type=0, value=0).put()
            DeliverySlot(name=u'Через 5 минут', slot_type=0, value=5).put()
            DeliverySlot(name=u'Через 10 минут', slot_type=0, value=10).put()
            DeliverySlot(name=u'Через 15 минут', slot_type=0, value=15).put()
            DeliverySlot(name=u'Через 20 минут', slot_type=0, value=20).put()
            DeliverySlot(name=u'Через 25 минут', slot_type=0, value=25).put()
            DeliverySlot(name=u'Через 30 минут', slot_type=0, value=30).put()
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
        if self.user is not None and self.user.get_role() == CompanyUser.ROLE:
            self.success()
        login = self.request.POST.get("login").lower().strip()
        password = self.request.POST.get("password")
        try:
            user_dict = self.auth.get_user_by_password(login, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.render('/login.html', login=login, error=u"Неверный логин или пароль")
        else:
            user = CompanyUser.get_by_id(user_dict["user_id"])
            if user.get_role() != CompanyUser.ROLE:
                self.render('/login.html', login=login, error=u"Неверный логин или пароль")
            else:
                self.success()


class LogoutHandler(CompanyBaseHandler):
    #@company_user_required
    def get(self):
        if "namespace" in self.session:
            del self.session["namespace"]
        self.auth.unset_session()
        self.redirect('/company/login')