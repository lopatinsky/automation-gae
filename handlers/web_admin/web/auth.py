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


class SignupHandler(BaseHandler):  # todo: deprecated, used only with namespace in the url
    @cached_property
    def venues(self):
        return Venue.query().fetch()

    def render(self, template_name, **values):
        super(SignupHandler, self).render(template_name, venues=self.venues, **values)

    def success(self):
        self.redirect("orders")

    def get(self):
        if self.user is not None:
            self.success()
        else:
            self.render('signup.html')

    def post(self):
        if self.user is not None:
            self.success()
        login, password, password2 = \
            self.request.get("email").strip().lower(), \
            self.request.get("password"), self.request.get("password2")
        venue_id = self.request.get_range("venue_id", default=-1)
        venue_ids = {v.key.id(): v.key for v in self.venues}
        error = None
        if not login:
            error = u"Не введен логин"
        elif not password:
            error = u"Не введен пароль"
        elif password != password2:
            error = u"Пароли не совпадают"
        elif venue_id and venue_id not in venue_ids:
            error = u"Неправильно выбрана кофейня"
        else:
            venue_key = venue_ids.get(venue_id, None)
            namespace = namespace_manager.get_namespace()
            success, user = Admin.create_user(login, namespace=namespace, venue=venue_key, password_raw=password)
            if success:
                set_current_user(self.auth, user)
                namespace_manager.set_namespace('')
                success, user = Admin.create_user(login, namespace=namespace, venue=venue_key, password_raw=password)
                if success:
                    logging.info(user)
            else:
                error = u"Пользователь с этим email уже зарегистрирован"
        if error:
            self.render('signup.html', email=login, error=error, venue_id=venue_id)
        else:
            self.success()


class LogoutHandler(BaseHandler):
    @user_required
    def get(self):
        self.auth.unset_session()
        self.redirect("login")
