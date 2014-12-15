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
        error_number = self.request.get("error_number")
        error_number = None if not error_number else int(error_number)
        sound_level_general = self.request.get("sound_level_general")
        sound_level_general = None if not sound_level_general else int(sound_level_general)
        sound_level_system = self.request.get("sound_level_system")
        sound_level_system = None if not sound_level_system else int(sound_level_system)
        is_in_charging = self.request.get("is_in_charging")
        is_in_charging = None if not is_in_charging else bool(int(is_in_charging))
        is_turned_on = self.request.get("is_turned_on")
        is_turned_on = None if not is_turned_on else bool(int(is_turned_on))
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
                                     is_turned_on=is_turned_on, app_version=app_version)
        history_item.put()
        self.render_json({})
