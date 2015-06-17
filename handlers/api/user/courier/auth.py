from webapp2_extras import security
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from handlers.api.user.courier.base import CourierBaseHandler
from methods.auth import api_courier_required
from models.user import Courier, CourierStatus

__author__ = 'dvpermyakov'


class LoginHandler(CourierBaseHandler):
    def post(self):
        login = self.request.get("login")
        password = self.request.get("password")
        try:
            user_dict = self.auth.get_user_by_password(login, password, save_session=False)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.abort(401)
        uid = user_dict["user_id"]
        courier = Courier.get_by_id(uid)
        if not courier or courier.get_role() != Courier.ROLE:
            self.abort(401)
        token = security.generate_random_string(entropy=256)
        full_token = "%s_%s" % (uid, token)
        CourierStatus.create(uid, token)
        self.render_json({"token": full_token})


class LogoutHandler(CourierBaseHandler):
    @api_courier_required
    def post(self):
        self._token_entity.key.delete()
        self.auth.unset_session()
        self.render_json({})