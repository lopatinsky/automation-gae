from google.appengine.api import mail, app_identity
from google.appengine.ext.ndb import GeoPt
from handlers.api.admin.base import AdminApiHandler
from methods import location
from methods.auth import api_user_required
from models import AdminStatus

_MAX_DISTANCE_ALLOWED = 0.5
_EMAIL_SENDER = "ping_errors@%s.appspotmail.com" % app_identity.get_application_id()


class PingHandler(AdminApiHandler):
    @api_user_required
    def post(self):
        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))
        geopt = GeoPt(lat, lon)

        status = AdminStatus.get(self.user.key.id(), self.token)
        distance = location.distance(geopt, status.location)
        if distance > _MAX_DISTANCE_ALLOWED:
            body = "Error: distance too large\n" \
                   "Initial coordinates: %s\n" \
                   "Current coordinates: %s\n" \
                   "Distance: %s km\n" \
                   "Email: %s" % (status.location, geopt, distance, self.user.email)
            mail.send_mail(_EMAIL_SENDER, "mdburshteyn@gmail.com", "[DoubleB] Ping error", body)  # TODO recipient
        status.put()
        self.render_json({})