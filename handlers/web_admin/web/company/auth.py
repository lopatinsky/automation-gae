# coding=utf-8
__author__ = 'dvpermyakov'

from ..base import BaseHandler


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
            success, user = self.auth.store.user_model.create_user(
                email, email=email, password_raw=password, venue=venue_key)
            if success:
                set_current_user(self.auth, user)
            else:
                error = u"Пользователь с этим email уже зарегистрирован"
        if error:
            self.render('signup.html', email=email, error=error, venue_id=venue_id)
        else:
            self.success()