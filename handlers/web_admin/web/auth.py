# coding=utf-8

from .base import BaseHandler
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from methods.auth import set_current_user, user_required


class LoginHandler(BaseHandler):
    def success(self):
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
        error = None
        if not email:
            error = u"Не введен email"
        elif not password:
            error = u"Не введен пароль"
        elif password != password2:
            error = u"Пароли не совпадают"
        else:
            success, user = self.auth.store.user_model.create_user(
                email, email=email, password_raw=password)
            if success:
                set_current_user(self.auth, user)
            else:
                error = u"Пользователь с этим email уже зарегистрирован"
        if error:
            self.render('signup.html', email=email, error=error)
        else:
            self.success()


class LogoutHandler(BaseHandler):
    @user_required
    def get(self):
        self.auth.unset_session()
        self.redirect("login")
