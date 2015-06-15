from google.appengine.ext.ndb import GeoPt
from handlers.api.user.admin.base import AdminApiHandler
from methods.auth import api_admin_required
from models import AdminStatus, TabletRequest


class PingHandler(AdminApiHandler):
    @api_admin_required
    def post(self):
        lat = float(self.request.get("lat"))
        lon = float(self.request.get("lon"))

        error_number = self.request.get_range("error_number")
        sound_level_general = self.request.get_range("sound_level_general")
        sound_level_system = self.request.get_range("sound_level_system")

        is_in_charging = self.request.get("is_in_charging", None)
        if is_in_charging:
            is_in_charging = is_in_charging == "true"

        is_turned_on = self.request.get("is_turned_on", None)
        if is_turned_on:
            is_turned_on = is_turned_on == "true"

        battery_level = self.request.get_range("battery_level")
        app_version = self.request.get("app_version", None)

        geopt = GeoPt(lat, lon)

        status = AdminStatus.get(self.user.key.id(), self.token)
        if status.location.lat == 0.0 and status.location.lon == 0.0:
            status.location = geopt
        status.put()

        if status.admin.venue and not status.readonly:
            history_item = TabletRequest(admin_id=status.admin.key.id(), token=self.token, location=geopt,
                                         error_number=error_number, sound_level_general=sound_level_general,
                                         sound_level_system=sound_level_system, is_in_charging=is_in_charging,
                                         is_turned_on=is_turned_on, app_version=app_version,
                                         battery_level=battery_level)
            history_item.put()
        self.render_json({})
