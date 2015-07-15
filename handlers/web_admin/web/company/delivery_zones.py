import json
import logging
from google.appengine.ext.ndb import GeoPt
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.auth import company_user_required
from methods.map import get_cities_by_coordinates, get_areas_by_coordinates
from models import DeliveryZone, STATUS_AVAILABLE, STATUS_UNAVAILABLE, Venue, Address
from models.venue import DELIVERY, GeoRib

__author__ = 'dvpermyakov'


class ListDeliveryZonesHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        zones = DeliveryZone.query().order(DeliveryZone.sequence_number).fetch()
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
                candidates = get_areas_by_coordinates(address.lat, address.lon)
                if candidates:
                    address.area = candidates[0]['address']['area']
                zone = DeliveryZone(address=address)
                zone.put()
                for delivery in venue.delivery_types:
                    if delivery.delivery_type == DELIVERY:
                        delivery.delivery_zones = [zone.key]
                venue.put()
                zones.append(zone)
        for zone in zones:
            zone.address_str = zone.address.str()
        self.render('/delivery_settings/delivery_zones.html', zones=zones, ZONE_MAP=DeliveryZone.SEARCH_MAP)

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


class AddingMapDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/delivery_settings/map.html')


class AddDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        lat = float(self.request.get('lat'))
        lon = float(self.request.get('lon'))
        candidates = get_cities_by_coordinates(lat, lon)
        if candidates:
            address = candidates[0]['address']
            address_obj = Address(**address)
            address_obj.lat = lat
            address_obj.lon = lon
            candidates = get_areas_by_coordinates(lat, lon)
            if candidates:
                address_obj.area = candidates[0]['address']['area']
            zone = DeliveryZone(address=address_obj)
            zone.sequence_number = DeliveryZone.generate_sequence_number()
            zone.put()
            self.redirect('/company/delivery/zone/list')
        else:
            self.redirect('/company/delivery/zone/add_by_map')


class EditDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        search_types = []
        for search_type in DeliveryZone.SEARCH_TYPES:
            search_types.append({
                'name': DeliveryZone.SEARCH_MAP[search_type],
                'value': search_type
            })
        self.render('/delivery_settings/edit_delivery_zones.html', zone=zone, search_types=search_types)

    @company_user_required
    def post(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        zone.search_type = self.request.get_range('search_type')
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


class UpDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        previous = zone.get_previous()
        if not previous:
            self.abort(400)
        number = previous.sequence_number
        previous.sequence_number = zone.sequence_number
        zone.sequence_number = number
        zone.put()
        previous.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'zone_id': zone.key.id(),
            'previous_id': previous.key.id()
        }, separators=(',', ':')))


class DownDeliveryZoneHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        zone_id = self.request.get_range('zone_id')
        zone = DeliveryZone.get_by_id(zone_id)
        if not zone:
            self.abort(400)
        next_ = zone.get_next()
        if not next_:
            self.abort(400)
        number = next_.sequence_number
        next_.sequence_number = zone.sequence_number
        zone.sequence_number = number
        zone.put()
        next_.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'zone_id': zone.key.id(),
            'next_id': next_.key.id()
        }, separators=(',', ':')))