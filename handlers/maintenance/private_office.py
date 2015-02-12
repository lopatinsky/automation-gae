# coding=utf-8

__author__ = 'dvpermyakov'

from base import BaseHandler
from models import Admin, Venue
from methods import auth
from webapp2_extras import security
import logging

SCOPE = "padmin"


class ListPAdmins(BaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        admins = []
        for venue in venues:
            admin = Admin.query(Admin.venue == venue.key, Admin.role == Admin.PRIVATE_OFFICE_ADMIN).get()
            if admin:
                admins.append(admin)
                continue
            auth_id = u'%s:%s' % (SCOPE, venue.title)
            password = security.generate_random_string(length=12)
            values = {
                'email': venue.title.strip().lower(),
                'venue': venue.key,
                'role': Admin.PRIVATE_OFFICE_ADMIN,
                'password_raw': password
            }
            success, info = self.auth.store.user_model.create_user(auth_id, **values)
            if success:
                admins.append(info.key.get())
            else:
                self.abort(500)
        admins = Admin.query(Admin.role == Admin.PRIVATE_OFFICE_ADMIN).fetch()
        self.render('private_office/admin_list.html', admins=admins)


class ChangeLoginPAdmins(BaseHandler):

    def get(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        self.render('/private_office/change_login.html', admin=admin)

    def post(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        login = self.request.get('login').strip().lower()
        values = {
            'email': login,
            'venue': admin.venue,
            'role': admin.role,
            'password_raw': admin.password
        }
        auth_id = u'%s:%s' % (SCOPE, login)
        success, info = self.auth.store.user_model.create_user(auth_id, **values)
        if success:
            admin.key.delete()
            self.redirect_to('padmin_main')
        else:
            self.render('/private_office/change_login.html', admin=admin, error=u'Логин занят')


class ChangePasswordPAdmin(BaseHandler):
    def get(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        self.render('/private_office/change_password.html', admin=admin)

    def post(self, admin_id):
        admin_id = int(admin_id)
        admin = Admin.get_by_id(admin_id)
        if not admin:
            self.abort(500)
        password = self.request.get('password')
        repeat_password = self.request.get('repeat_password')
        if password != repeat_password:
            self.render('/private_office/change_password.html', admin=admin, error=u'Пароли не совпадают')
        else:
            auth.set_password(admin, password)
            admin.put()
            self.redirect_to('padmin_main')