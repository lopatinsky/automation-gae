from .base import BaseHandler
from methods.auth import set_password
from models import Admin


class AdminsHandler(BaseHandler):
    def get(self):
        admins = Admin.query().fetch()
        admins = sorted(admins, key=lambda a: a.email)
        self.render('admins.html', admins=admins)

    def post(self):
        admins = Admin.query().fetch()
        admins = sorted(admins, key=lambda a: a.email)
        admin_id = self.request.get_range("admin_id")
        password = self.request.get("password")
        success = False
        for admin in admins:
            if admin.key.id() == admin_id:
                set_password(admin, password)
                admin.put()
                success = True
                break
        self.render('admins.html', admins=admins, success=success)
