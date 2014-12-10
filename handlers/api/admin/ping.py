import logging
from google.appengine.ext.ndb import GeoPt
from handlers.api.admin.base import AdminApiHandler
from methods import location, email
from methods.auth import api_user_required
from models import AdminStatus, TabletQuery

_MAX_DISTANCE_ALLOWED = 0.5


def _is_valid(location):
    return location.lat != 0 or location.lon != 0


class PingHandler(AdminApiHandler):
    @api_user_required
    def post(self):
        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))
        geopt = GeoPt(lat, lon)

        status = AdminStatus.get(self.user.key.id(), self.token)
        status_location_is_valid = _is_valid(status.location)
        if not status_location_is_valid:  # GPS was disabled on startup, app sent zero coordinates
            status.location = geopt

        distance = location.distance(geopt, status.location)
        if distance > _MAX_DISTANCE_ALLOWED:
            body = "Error: distance too large\n" \
                   "Initial coordinates: %s\n" \
                   "Current coordinates: %s\n" \
                   "Distance: %s km\n" \
                   "Login: %s\n"\
                   "Token: %s" % (status.location, geopt, distance, self.user.email, status.key.id())
            logging.error(body)
            email.send_error("ping", "Ping error", body)
        status.put()
        history_item = TabletQuery(admin_id=status.admin.key.id(), token=self.token, location=status.location)
        history_item.put()
        self.render_json({})
