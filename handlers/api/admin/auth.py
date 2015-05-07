from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import GeoPt
from webapp2_extras import security
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from .base import AdminApiHandler
from methods.auth import api_user_required
from models import AdminStatus


class LoginHandler(AdminApiHandler):
    def post(self):
        email = self.request.get("email")
        password = self.request.get("password")
        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))
        readonly = self.request.get("readonly") == "true"
        try:
            user_dict = self.auth.get_user_by_password(email, password, save_session=False)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.abort(401)
        uid = user_dict["user_id"]
        token = security.generate_random_string(entropy=256)
        full_token = "%s_%s" % (uid, token)
        AdminStatus.create(uid, token, GeoPt(lat, lon), readonly)
        self.render_json({"token": full_token})


class LogoutHandler(AdminApiHandler):
    @api_user_required
    def post(self):
        namespace_manager.set_namespace('')
        password = self.request.get("password")
        try:
            self.auth.store.validate_password(self.user.login, password)
        except (InvalidAuthIdError, InvalidPasswordError):
            self.abort(403)
        AdminStatus.get(self.user.key.id(), self.token).key.delete()
        self.render_json({})