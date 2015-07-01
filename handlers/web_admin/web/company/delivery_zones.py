import logging
from google.appengine.ext.ndb import GeoPt
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.auth import company_user_required
from models import DeliveryZone, STATUS_AVAILABLE, STATUS_UNAVAILABLE, Venue
from models.venue import DELIVERY, GeoRib

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
        zone.comment = self.request.get('comment')
        zone.put()
        self.redirect('/company/delivery/zone/list')


class MapDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        values = {
            'zone': zone,
            'lat': zone.address.lat,
            'lon': zone.address.lon,
            'name': zone.address.str(),
            'coords': zone.polygon
        }
        self.render('/delivery_settings/restriction_map.html', **values)

    @company_user_required
    def post(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        logging.info(zone)
        polygon = self.request.get('polygon').split(',')
        polygon = [point for point in polygon if point]
        logging.info(polygon)

        def get_point(index):
            lat = float(polygon[index])
            index += 1
            lon = float(polygon[index])
            index += 1
            point = GeoPt(lat=lat, lon=lon)
            return point, index

        i = 0
        old_point = None
        ribs = []
        while i < len(polygon):
            point, i = get_point(i)
            if old_point:
                ribs.append(GeoRib(point1=old_point, point2=point))
            old_point = point
        zone.geo_ribs = ribs
        logging.info(ribs)
        zone.put()
        self.redirect('/company/delivery/zone/list')