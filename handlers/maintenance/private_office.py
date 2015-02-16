# coding=utf-8

__author__ = 'dvpermyakov'

from base import BaseHandler
from models import Admin, Venue
from methods import auth
import logging


class ListPAdmins(BaseHandler):
    def get(self):
        admins = [a
                  for a in Admin.query().fetch()
                  if a.auth_ids[0].startswith(Admin.PADMIN)]
        admins = sorted(admins, key=lambda a: a.login)
        self.render('private_office/admin_list.html', admins=admins)


class AutoCreatePAdmins(BaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        for venue in venues:
            cur_admin = None
            for admin in Admin.query(Admin.venue == venue.key).fetch():
                if Admin.PADMIN in admin.auth_ids[0]:
                    cur_admin = admin
                    break
            if cur_admin:
                continue

            ru = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            en = u'abvgdeegziyklmnoprstufhzcss_y_eua'
            trans_dict = dict(zip(ru, en))

            login_rus = [c for c in venue.title.lower() if 'a' <= c <= 'z' or u'а' <= c <= u'я']
            login_en = ''.join(trans_dict.get(c, c) for c in login_rus)

            auth_id = '%s:%s' % (Admin.PADMIN, login_en)
            values = {
                'email': login_en,
                'venue': venue.key,
                'password_raw': '0000'
            }
            success, info = Admin.create_user(auth_id, **values)
            if not success:
                self.abort(500)
        self.redirect_to("padmin_main")


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
        }
        auth_id = '%s:%s' % (Admin.PADMIN, login)
        success, info = Admin.create_user(auth_id, **values)
        if success:
            info.password = admin.password
            info.put()
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
        auth.set_password(admin, password)
        admin.put()
        self.redirect_to('padmin_main')
