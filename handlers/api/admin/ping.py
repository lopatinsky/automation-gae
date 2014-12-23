import logging
from google.appengine.ext.ndb import GeoPt
from handlers.api.admin.base import AdminApiHandler
from methods import location, email
from methods.auth import api_user_required
from models import AdminStatus, TabletRequest

_MAX_DISTANCE_ALLOWED = 0.5


def _is_valid(location):
    return location.lat != 0 or location.lon != 0


class PingHandler(AdminApiHandler):
    @api_user_required
    def post(self):
        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))

        error_number = self.request.get_range("error_number")

        sound_level_general = self.request.get_range("sound_level_general")

        sound_level_system = self.request.get_range("sound_level_system")

        is_in_charging = self.request.get("is_in_charging")
        if not is_in_charging is None:
            is_in_charging = bool(is_in_charging)

        is_turned_on = self.request.get("is_turned_on")
        if not is_turned_on is None:
            is_turned_on = bool(is_turned_on)

        battery_level = self.request.get_range("battery_level")

        app_version = self.request.get("app_version")
        if not app_version:
            app_version = None

        geopt = GeoPt(lat, lon)

        status = AdminStatus.get(self.user.key.id(), self.token)
        status_location_is_valid = _is_valid(status.location)
        if not status_location_is_valid:  # GPS was disabled on startup, app sent zero coordinates
            status.location = geopt

        distance = location.distance(geopt, status.location)
        if _is_valid(geopt) and distance > _MAX_DISTANCE_ALLOWED:
            body = "Error: distance too large\n" \
                   "Initial coordinates: %s\n" \
                   "Current coordinates: %s\n" \
                   "Distance: %s km\n" \
                   "Login: %s\n"\
                   "Token: %s" % (status.location, geopt, distance, self.user.email, status.key.id())
            logging.error(body)
            email.send_error("ping", "Ping error", body)
        status.put()
        history_item = TabletRequest(admin_id=status.admin.key.id(), token=self.token, location=geopt,
                                     error_number=error_number, sound_level_general=sound_level_general,
                                     sound_level_system=sound_level_system, is_in_charging=is_in_charging,
                                     is_turned_on=is_turned_on, app_version=app_version, battery_level=battery_level)
        history_item.put()
        self.render_json({})
