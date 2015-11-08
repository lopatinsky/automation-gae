import json

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb

from .base import ApiHandler
from methods.client import save_city
from methods.geocoder import get_cities_by_coordinates
from methods.rendering import get_location
from models.config.config import config, RESTO_APP
from methods.proxy.resto.registration import resto_registration
from models import STATUS_AVAILABLE
from methods.branch_io import INVITATION, GIFT
from models.proxy.unified_app import AutomationCompany, ProxyCity
from models.share import SharedPromo, Share, SharedGift
from models.client import IOS_DEVICE, ANDROID_DEVICE, Client
from models.order import Order


def _refresh_client_info(request, response, android_id, device_phone, client_id=None, city_id=None):
    def refresh(client):
        client.user_agent = request.headers["User-Agent"]
        if 'iOS' in client.user_agent:
            client.device_type = IOS_DEVICE
        elif 'Android' in client.user_agent:
            client.device_type = ANDROID_DEVICE
        if android_id:
            client.android_id = android_id
        if device_phone and not client.tel:
            client.tel = device_phone
        if client.city and client.city.id() == city_id:
            response['show_cities'] = False
        else:
            response['show_cities'] = True
        if city_id:
            save_city(client, city_id)
        client.put()
        client.save_session()

    current_namespace = namespace_manager.get_namespace()
    if request.init_namespace:
        namespace_manager.set_namespace(request.init_namespace)
    if client_id:
        client = Client.get_by_id(client_id)
    else:
        client = Client.create()
        client_id = client.key.id()
    refresh(client)
    if request.init_namespace:
        namespace_manager.set_namespace(request.init_namespace)
        for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch():
            namespace_manager.set_namespace(company.namespace)
            other_client = Client.get_by_id(client_id)
            if not other_client:
                other_client = Client.create(client_id)
            refresh(other_client)
    namespace_manager.set_namespace(current_namespace)
    return client


def _perform_registration(request):
    response = {}

    client_id = request.get_range('client_id') or int(request.headers.get('Client-Id') or 0)
    android_id = request.get('android_id')
    device_phone = request.get('device_phone')
    location = get_location(request.get("ll"))

    city_id = None
    if location:
        candidates = get_cities_by_coordinates(location.lat, location.lon)
        if candidates:
            city_id = ProxyCity.get_city_id(candidates[0]['address']['city'])
            if city_id:
                response['location_city_id'] = str(city_id)

    client = None
    if client_id:
        client = Client.get_by_id(client_id)
    else:
        if android_id:
            client = Client.query(Client.android_id == android_id).get()
        if client:
            client_id = client.key.id()  # it is need to share gift

    if not client:
        client = _refresh_client_info(request, response, android_id, device_phone, city_id=city_id)
    else:
        client = _refresh_client_info(request, response, android_id, device_phone, client_id, city_id=city_id)

    response['client_id'] = client.key.id()
    client_name = client.name or ''
    if client.surname:
        client_name += ' ' + client.surname
    response['client_name'] = client_name
    response['client_email'] = client.email or ''

    share_data = request.get('share_data')

    if share_data:
        share_data = json.loads(share_data)
        share_id = share_data.get('share_id')
        if share_id:
            share = Share.get_by_id(int(share_id))
            response["share_type"] = share.share_type
            if share.share_type == INVITATION:
                if not client_id or \
                        (not Order.query(Order.client_id == client_id).get() and client_id != share.sender.id()):
                    promo = SharedPromo.query(SharedPromo.recipient == client.key).get()
                    if not promo:
                        SharedPromo(sender=share.sender, recipient=client.key, share_id=share.key.id()).put()
            elif share.share_type == GIFT:
                if share.status == Share.ACTIVE:
                    gift = SharedGift.query(SharedGift.share_id == share.key.id()).get()
                    if gift.status == SharedGift.READY:
                        gift.perform(client, namespace_manager.get_namespace())
                    response['branch_name'] = share_data.get('name')
                    response['branch_phone'] = share_data.get('phone')
    return response


class RegistrationHandler(ApiHandler):
    def post(self):
        response = _perform_registration(self.request)
        client = Client.get_by_id(response['client_id'])
        if config.APP_KIND == RESTO_APP:
            resto_registration(client)
        self.render_json(response)
