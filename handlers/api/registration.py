import json

from google.appengine.api.namespace_manager import namespace_manager

from .base import ApiHandler
from models.config.config import config, RESTO_APP
from methods.proxy.resto.registration import resto_registration
from models import STATUS_AVAILABLE
from methods.branch_io import INVITATION, GIFT
from models.proxy.unified_app import AutomationCompany
from models.share import SharedPromo, Share, SharedGift
from models.client import IOS_DEVICE, ANDROID_DEVICE, Client
from models.order import Order


def _refresh_client_info(request, android_id, device_phone, client_id=None):
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
        client.put()
        client.save_session()

    current_namespace = namespace_manager.get_namespace()
    client = None
    if client_id:
        if request.init_namespace:
            namespace_manager.set_namespace(request.init_namespace)
        client = Client.get(client_id)
    if not client:
        client = Client.create()
        client_id = client.key.id()
    refresh(client)
    if request.init_namespace and not Client.is_id_global(client_id):
        namespace_manager.set_namespace(request.init_namespace)
        for company in AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).fetch():
            namespace_manager.set_namespace(company.namespace)
            other_client = Client.get(client_id)
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

    client = None
    client_existed = False
    if client_id:
        client = Client.get(client_id)
    elif android_id:
        client = Client.find_by_android_id(android_id)
        if client:
            client_id = client.key.id()

    if client:
        client_existed = True
    else:
        client_id = None

    client = _refresh_client_info(request, android_id, device_phone, client_id)

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
                if not client_existed or \
                        (not Order.query(Order.client_id == client_id).get() and client.key.id() != share.sender.id()):
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
    return response, client


class RegistrationHandler(ApiHandler):
    def post(self):
        response, client = _perform_registration(self.request)
        if config.APP_KIND == RESTO_APP:
            resto_registration(client)
        self.render_json(response)
