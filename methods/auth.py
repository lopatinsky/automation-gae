from webapp2_extras import security
from models import CompanyUser, Admin
from models.user import Courier


def set_current_user(auth, user):
    user_dict = auth.store.user_to_dict(user)
    auth.set_session(user_dict)


def set_password(user, password):
    user.password = security.generate_password_hash(password, length=12)


def user_required(handler):  # it is for web barista (not used)
    def check_user(self, *args, **kwargs):
        if self.user is None or self.user.get_role() != Admin.ROLE:
            self.redirect("/admin/login")
        else:
            return handler(self, *args, **kwargs)
    return check_user


def api_admin_required(handler):  # it is for api barista
    def check_user(self, *args, **kwargs):
        if self.user is None or self.user.get_role() != Admin.ROLE:
            self.abort(401)
        else:
            return handler(self, *args, **kwargs)
    return check_user


def api_courier_required(handler):  # it is for api courier
    def check_user(self, *args, **kwargs):
        if self.user is None or self.user.get_role() != Courier.ROLE:
            self.abort(401)
        else:
            return handler(self, *args, **kwargs)
    return check_user


def company_user_required(handler):
    def check_user(self, *args, **kwargs):
        if self.user is None or self.user.get_role() != CompanyUser.ROLE:
            self.redirect_to('company_login')
        else:
            return handler(self, *args, **kwargs)
    return check_user


def write_access_required(handler):
    def check_user(self, *args, **kwargs):
        if self._token_entity.readonly:
            self.abort(403)
        else:
            return handler(self, *args, **kwargs)
    return check_user
