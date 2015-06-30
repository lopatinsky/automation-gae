from handlers.web_admin.web.company import CompanyBaseHandler
from methods.auth import company_user_required
from models import DeliveryZone, STATUS_AVAILABLE, STATUS_UNAVAILABLE, Venue
from models.venue import DELIVERY

__author__ = 'dvpermyakov'


class ListDeliveryZonesHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        zones = DeliveryZone.query().fetch()
        for venue in Venue.query(Venue.active == True).fetch():
            found = False
            for zone in zones:
                if zone.address.city == venue.address.city:
                    if zone.address.street == venue.address.street:
                        if zone.address.home == venue.address.home:
                            found = True
            if not found:
                address = venue.address
                address.lat = venue.coordinates.lat
                address.lon = venue.coordinates.lon
                zone = DeliveryZone(address=address)
                zone.put()
                for delivery in venue.delivery_types:
                    if delivery.delivery_type == DELIVERY:
                        delivery.delivery_zones = [zone.key]
                venue.put()
                zones.append(zone)
        for zone in zones:
            zone.address_str = zone.address.str()
        self.render('/delivery_settings/delivery_zones.html', zones=zones)

    @company_user_required
    def post(self):
        zones = DeliveryZone.query().fetch()
        for zone in zones:
            confirmed = bool(self.request.get(str(zone.key.id())))
            if confirmed:
                zone.status = STATUS_AVAILABLE
            else:
                zone.status = STATUS_UNAVAILABLE
            zone.put()
        self.redirect('/company/main')


class EditDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        self.render('/delivery_settings/edit_delivery_zones.html', zone=zone)

    @company_user_required
    def post(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        zone.min_sum = self.request.get_range('min_sum')
        zone.price = self.request.get_range('price')
        zone.put()
        self.redirect('/company/delivery/zone/list')