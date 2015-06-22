import json
from google.appengine.api.namespace_manager import namespace_manager
from .base import ApiHandler
from models import Client, Share, SharedGift, STATUS_AVAILABLE
from methods.branch_io import INVITATION, GIFT
from models.proxy.unified_app import AutomationCompany
from models.share import SharedPromo
from models.client import IOS_DEVICE, ANDROID_DEVICE


def _refresh_client_info(request, device_phone, client_id=None):
    def refresh(client):
        client.user_agent = request.headers["User-Agent"]
        if 'iOS' in client.user_agent:
            client.device_type = IOS_DEVICE
        elif 'Android' in client.user_agent:
            client.device_type = ANDROID_DEVICE
        if device_phone:
            client.device_phone = device_phone
        client.put()

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

    client_id = request.get_range('client_id')
    device_phone = "".join(c for c in request.get('device_phone') if '0' <= c <= '9')

    client = None
    if client_id:
        client = Client.get_by_id(client_id)
    else:
        if device_phone:
            client = Client.query(Client.device_phone == device_phone).get()
            if client:
                client_id = client.key.id()  # it is need to share gift

    if not client:
        client = _refresh_client_info(request, device_phone)
    else:
        client = _refresh_client_info(request, device_phone, client_id)

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
            share = Share.get_by_id(share_id)
            response["share_type"] = share.share_type
            if share.share_type == INVITATION:
                if not client_id:
                    SharedPromo(sender=share.sender, recipient=client.key, share_id=share.key.id()).put()
            elif share.share_type == GIFT:
                if share.status == Share.ACTIVE:
                    gift = SharedGift.query(SharedGift.share_id == share.key.id()).get()
                    if gift.status == SharedGift.READY:
                        gift.deactivate(client, namespace_manager.get_namespace())
                    response['branch_name'] = share_data.get('name')
                    response['branch_phone'] = share_data.get('phone')
    return response


class RegistrationHandler(ApiHandler):
    def post(self):
        response = _perform_registration(self.request)
        self.render_json(response)
