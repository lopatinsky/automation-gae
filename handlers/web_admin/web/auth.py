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
        logging.info(self.user)
        if hasattr(self.user, 'role') and self.user.role == Admin.PRIVATE_OFFICE_ADMIN:
            self.redirect_to('padmin_report')
        else:
            self.redirect("orders.php")

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


class SignupHandler(BaseHandler):
    @cached_property
    def venues(self):
        return Venue.query().fetch()

    def render(self, template_name, **values):
        super(SignupHandler, self).render(template_name, venues=self.venues, **values)

    def success(self):
        self.redirect("orders.php")

    def get(self):
        if self.user is not None:
            self.success()
        else:
            self.render('signup.html')

    def post(self):
        if self.user is not None:
            self.success()
        email, password, password2 = \
            self.request.get("email").strip().lower(), \
            self.request.get("password"), self.request.get("password2")
        venue_id = self.request.get_range("venue_id", default=-1)
        venue_ids = {v.key.id(): v.key for v in self.venues}
        error = None
        if not email:
            error = u"Не введен email"
        elif not password:
            error = u"Не введен пароль"
        elif password != password2:
            error = u"Пароли не совпадают"
        elif venue_id and venue_id not in venue_ids:
            error = u"Неправильно выбрана кофейня"
        else:
            venue_key = venue_ids.get(venue_id, None)
            success, user = Admin.create_user(email, email=email, password_raw=password, venue=venue_key)
            if success:
                set_current_user(self.auth, user)
            else:
                error = u"Пользователь с этим email уже зарегистрирован"
        if error:
            self.render('signup.html', email=email, error=error, venue_id=venue_id)
        else:
            self.success()


class LogoutHandler(BaseHandler):
    @user_required
    def get(self):
        self.auth.unset_session()
        self.redirect("login")
