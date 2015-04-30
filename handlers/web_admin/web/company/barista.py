# coding=utf-8
import logging
from google.appengine.api.namespace_manager import namespace_manager
from webapp2 import cached_property

__author__ = 'dvpermyakov'

from base import CompanyBaseHandler
from models import Admin, Venue
from methods import auth


class SignupHandler(CompanyBaseHandler):
    @cached_property
    def venues(self):
        return Venue.query().fetch()

    def render(self, template_name, **values):
        super(SignupHandler, self).render(template_name, venues=self.venues, **values)

    def success(self):
        self.redirect_to("barista_main")

    def get(self):
        self.render('/barista/signup.html')

    def post(self):
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
            values = {
                'login': login,
                'namespace': self.user.namespace,
                'venue': venue_key,
                'password_raw': password
            }
            success, user = Admin.create_user(login, **values)
            if success:
                values.update({
                    'namespace': ''
                })
                namespace_manager.set_namespace('')
                success, user = Admin.create_user(login, **values)
                if success:
                    logging.info(user)
            else:
                error = u"Пользователь с этим email уже зарегистрирован"
        if error:
            self.render('/barista/signup.html', email=login, error=error, venue_id=venue_id)
        else:
            self.success()


class ListAdmins(CompanyBaseHandler):
    def get(self):
        admins = Admin.query().fetch()
        admins = sorted(admins, key=lambda a: a.login)
        self.render('/barista/admin_list.html', admins=admins)


class AutoCreateAdmins(CompanyBaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        for venue in venues:
            admin = Admin.query(Admin.venue == venue.key).get()
            if admin:
                continue

            ru = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            en = u'abvgdeegziyklmnoprstufhzcss_y_eua'
            trans_dict = dict(zip(ru, en))

            login_rus = [c for c in venue.title.lower() if 'a' <= c <= 'z' or u'а' <= c <= u'я']
            login_en = ''.join(trans_dict.get(c, c) for c in login_rus)

            auth_id = login_en
            values = {
                'login': login_en,
                'venue': venue.key,
                'namespace': self.user.namespace,
                'password_raw': '0000'
            }
            success, info = Admin.create_user(auth_id, **values)
            if not success:
                self.abort(500)
        self.redirect_to("barista_main")


class ChangeLoginAdmins(CompanyBaseHandler):

    def get(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        self.render('/barista/change_login.html', admin=admin)

    def post(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        login = self.request.get('login').strip().lower()
        values = {
            'email': login,
            'venue': admin.venue,
        }
        success, info = Admin.create_user(login, **values)
        if success:
            info.password = admin.password
            info.put()
            admin.delete_auth_ids()
            admin.key.delete()
            self.redirect_to('padmin_main')
        else:
            self.render('/barista/change_login.html', admin=admin, error=u'Логин занят')


class ChangePasswordAdmin(CompanyBaseHandler):
    def get(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        self.render('/barista/change_password.html', admin=admin)

    def post(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        password = self.request.get('password')
        auth.set_password(admin, password)
        admin.put()
        self.redirect_to('barista_main')
