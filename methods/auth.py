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


class check_rights_decorator(object):
    bits = ()

    def __init__(self, bits):
        self.bits = bits

    def __call__(self, handler_method):
        def check_user(handler, *args, **kwargs):
            if handler.user is None or handler.user.get_role() != CompanyUser.ROLE:
                handler.redirect_to('company_login')
            elif not handler.user.has_rights(self.bits):
                handler.abort(403)
            else:
                return handler_method(handler, *args, **kwargs)

        return check_user


company_user_required = check_rights_decorator(())
full_rights_required = check_rights_decorator(CompanyUser.ALL_RIGHTS_BITS)

report_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_REPORT,))
venue_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_VENUE,))
menu_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_MENU,))
payment_types_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_PAYMENT_TYPE,))
promos_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_PROMOS,))
barista_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_BARISTA,))
promo_code_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_PROMO_CODE,))
company_info_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_COMPANY_INFO,))
legal_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_LEGAL,))
delivery_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_DELIVERY,))
delivery_types_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_DELIVERY_TYPES,))
zones_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_ZONES,))
news_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_NEWS,))
pushes_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_PUSHES,))
alfa_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_ALFA,))
user_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_USERS,))
config_rights_required = check_rights_decorator((CompanyUser.RIGHTS_BIT_CONFIG,))


def write_access_required(handler):
    def check_user(self, *args, **kwargs):
        if self._token_entity.readonly:
            self.abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_user
