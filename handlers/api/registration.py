import json
import logging
from .base import ApiHandler
from models import Client, Share, SharedGift
from methods.branch_io import INVITATION, GIFT
from models.share import SharedPromo


def perform_registration(request):
    response = {}

    request_client_id = client_id = request.get_range('client_id')
    device_phone = "".join(c for c in request.get('device_phone') if '0' <= c <= '9')

    client = None
    try:
        client = Client.get_by_id(client_id)
    except:
        pass
    if not client and device_phone:
        client = Client.query(Client.device_phone == device_phone).get()

    if client:  # getting client_id if client has device phone
        request_client_id = client.key.id()

    if not client:
        client = Client.create()
        client.user_agent = request.headers["User-Agent"]
        client.device_phone = device_phone
        client.put()
        logging.info("issued new client_id: %s", client.key.id())
    elif device_phone and device_phone != client.device_phone:
        client.device_phone = device_phone
        client.put()

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
                if not request_client_id:
                    SharedPromo(sender=share.sender, recipient=client.key, share_id=share.key.id()).put()
            elif share.share_type == GIFT:
                if share.status == Share.ACTIVE:
                    gift = SharedGift.query(SharedGift.share_id == share.key.id()).get()
                    if gift.status == SharedGift.READY:
                        gift.deactivate(client)
                    response['branch_name'] = share_data.get('name')
                    response['branch_phone'] = share_data.get('phone')
    return response


class RegistrationHandler(ApiHandler):
    def post(self):
        response = perform_registration(self.request)
        self.render_json(response)
