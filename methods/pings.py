from datetime import datetime
from datetime import timedelta
from methods import location
from models import TabletRequest

LEVEL_SUPPRESSED = -1
LEVEL_OK = 0
LEVEL_WARNING = 1
LEVEL_ERROR = 2
LEVEL_CRITICAL = 3

LEVELS_STRING_MAP = {
    LEVEL_WARNING: 'WARNING',
    LEVEL_ERROR: 'ERROR',
    LEVEL_CRITICAL: 'CRITICAL'
}


def _high_value_level(value, max_critical, max_error, max_warning):
    if value <= max_critical:
        return LEVEL_CRITICAL
    if value <= max_error:
        return LEVEL_ERROR
    if value <= max_warning:
        return LEVEL_WARNING
    return LEVEL_OK


def _low_value_level(value, min_critical, min_error, min_warning):
    return _high_value_level(-value, -min_critical, -min_error, -min_warning)


def _valid_location(p):
    return p.lat != 0 or p.lon != 0


def _collect_min(values, func):
    values = [func(x) for x in values]
    filtered = [x for x in values if x is not None]
    if filtered:
        return min(filtered)
    return None


class PingReport(object):
    errors = None  # list: [(level, message)]
    admin_status = None
    pings_10min = None
    last_ping = None
    suppressed = False

    # global info
    app_version = None
    error_number = None

    # worst ping info
    distance = None
    sound_level_system = None
    battery_level = None
    charging = None
    turned_on = None

    def _add_error(self, level, message):
        if level > LEVEL_OK:
            self.errors.append((level, message))

    def __init__(self, admin_status):
        self.admin_status = admin_status
        self.errors = []

        self._get_pings()

        self._check_suppressed()
        self._add_global_errors()
        if self.last_ping:
            self.app_version = self.last_ping.app_version
            self._collect_worst_info()
            self._check_worst_info()

    def _get_pings(self):
        self.pings_10min = TabletRequest.query(TabletRequest.token == self.admin_status.token,
                                               TabletRequest.request_time > datetime.now() - timedelta(minutes=10)) \
            .order(-TabletRequest.request_time).fetch()
        if self.pings_10min:
            self.last_ping = self.pings_10min[0]
        else:
            self.last_ping = TabletRequest.query(TabletRequest.token == self.admin_status.token)\
                .order(-TabletRequest.request_time).get()

    def _check_suppressed(self):
        venue_key = self.admin_status.admin.venue
        if self.admin_status.readonly or venue_key is None:
            self.suppressed = True
        else:
            venue = venue_key.get()
            if not venue.active or not venue.is_open():
                self.suppressed = True

    def _add_global_errors(self):
        if not self.last_ping:
            self._add_error(LEVEL_CRITICAL, "No pings found for this token")

        ping_count = len(self.pings_10min)
        ping_error_level = _high_value_level(ping_count, 1, 5, 8)
        self._add_error(ping_error_level, "Too few pings in last 10 minutes: %s" % ping_count)

        self.error_number = 0
        for ping in self.pings_10min:
            if ping.error_number is not None:
                self.error_number += ping.error_number
        error_number_level = _low_value_level(self.error_number, 10, 5, 1)
        self._add_error(error_number_level, "Request errors in the last 10 minutes: %s" % self.error_number)

    def _collect_worst_info(self):
        pings_to_collect = self.pings_10min
        if not pings_to_collect:
            pings_to_collect = [self.last_ping]

        self.sound_level_system = _collect_min(pings_to_collect, lambda ping: ping.sound_level_system)
        self.battery_level = _collect_min(pings_to_collect, lambda ping: ping.battery_level)
        self.charging = _collect_min(pings_to_collect, lambda ping: ping.is_in_charging)
        self.turned_on = _collect_min(pings_to_collect, lambda ping: ping.is_turned_on)

        initial_location = self.admin_status.location
        if _valid_location(initial_location):
            self.distance = -1
            for ping in pings_to_collect:
                if not _valid_location(ping.location):
                    self.distance = None
                    break
                distance = location.distance(initial_location, ping.location)
                if distance > self.distance:
                    self.distance = distance
            if self.distance is not None and self.distance < 0:
                self.distance = None

    def _check_worst_info(self):
        if not _valid_location(self.admin_status.location):
            self._add_error(LEVEL_WARNING, "No GPS lock")
        elif self.distance is None:
            self._add_error(LEVEL_WARNING, "GPS lock lost")
        else:
            distance_error_level = _low_value_level(self.distance, 2, 1, 0.5)
            self._add_error(distance_error_level, "Distance too large: %s" % self.distance)

        if self.app_version is None:
            self._add_error(LEVEL_ERROR, "Outdated app version: %s" % self.app_version)
            return

        if self.charging is False:
            self._add_error(LEVEL_WARNING, "Tablet not charging")

        if self.turned_on is False:
            self._add_error(LEVEL_CRITICAL, "Tablet turned off")

        if self.app_version == "1.1":
            sound_max = 15
        else:
            sound_max = 100
        sound_level = _high_value_level(1.0 * self.sound_level_system / sound_max, 0.2, 0.4, 0.6)
        self._add_error(sound_level, "Low sound volume: %s out of %s" % (sound_level, sound_max))

        # TODO add battery level after it's fixed (broken in 1.1)

    @property
    def error_level(self):
        if self.suppressed:
            return LEVEL_SUPPRESSED
        if not self.errors:
            return LEVEL_OK
        return max(level for level, message in self.errors)

    @property
    def error_messages(self):
        sorted_errors = sorted(self.errors, key=lambda e: e[0], reverse=True)
        return ["[%s] %s" % (LEVELS_STRING_MAP[level], message) for level, message in sorted_errors]
