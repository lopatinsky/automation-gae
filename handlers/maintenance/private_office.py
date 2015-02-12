# coding=utf-8

__author__ = 'dvpermyakov'

from base import BaseHandler
from models import Admin, Venue
from methods import auth
import logging


class ListPAdmins(BaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        admins = []
        for venue in venues:
            cur_admin = None
            for admin in Admin.query(Admin.venue == venue.key).fetch():
                if Admin.PADMIN in admin.auth_ids[0]:
                    cur_admin = admin
                    continue
            if cur_admin:
                admins.append(cur_admin)
                continue
            auth_id = '%s:%s' % (Admin.PADMIN, venue.title.strip().lower())
            values = {
                'email': venue.title.strip().lower(),
                'venue': venue.key,
                'password_raw': venue.title.strip().lower()
            }
            success, info = Admin.create_user(auth_id, **values)
            if success:
                admins.append(info.key.get())
            else:
                self.abort(500)
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
            'password_raw': login
        }
        auth_id = '%s:%s' % (Admin.PADMIN, login)
        success, info = Admin.create_user(auth_id, **values)
        if success:
            admin.delete_auth_ids()
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