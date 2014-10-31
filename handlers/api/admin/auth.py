from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from .base import AdminApiHandler
from methods.auth import api_user_required


class LoginHandler(AdminApiHandler):
    def post(self):
        email = self.request.get("email")
        password = self.request.get("password")
        try:
            user_dict = self.auth.get_user_by_password(email, password, save_session=False)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.abort(401)
        uid = user_dict["user_id"]
        token = self.auth.store.create_auth_token(uid)
        full_token = "%s_%s" % (uid, token)
        self.render_json({"token": full_token})


class LogoutHandler(AdminApiHandler):
    @api_user_required
    def post(self):
        password = self.request.get("password")
        try:
            self.auth.store.validate_password(self.user.email, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.abort(403)
        self.auth.store.delete_auth_token(self.user.key.id(), self.token)
        self.render_json({})
