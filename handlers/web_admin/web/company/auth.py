# coding=utf-8
import logging
from google.appengine.ext.ndb import metadata

__author__ = 'dvpermyakov'

from ..base import BaseHandler
from models import CompanyUser
from methods.rendering import latinize


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
            success, user = CompanyUser.create_user(login, namespace=namespace, login=login, password_raw=password)
            if not success:
                error = u"Пользователь с этим email уже зарегистрирован"
            self.redirect('/mt/automation')
        if error:
            logging.info(error)
            self.render('signup.html', email=login, error=error)
        else:
            self.success()