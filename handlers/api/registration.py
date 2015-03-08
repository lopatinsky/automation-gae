import json
import logging
from .base import ApiHandler
from models import Client, Share, SharedFreeCup, SharedGift


def perform_registration(request):
    response = {}

    client_id = request.get_range('client_id')
    device_phone = "".join(c for c in request.get('device_phone') if '0' <= c <= '9')

    client = None
    try:
        client = Client.get_by_id(client_id)
    except:
        pass
    if not client and device_phone:
        client = Client.query(Client.device_phone == device_phone).get()

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
        share = None
        if share_id:
            share = Share.get_by_id(share_id)

        if share:
            response["share_type"] = share.share_type
            if share.share_type == Share.INVITATION:
                existing_cup = SharedFreeCup(recipient=client.key)
                if not existing_cup:
                    SharedFreeCup(sender=share.sender, recipient=client.key, share_id=share.key.id()).put()
            elif share.share_type == Share.GIFT:
                if share.status == Share.ACTIVE:
                    gift = SharedGift.query(SharedGift.share_id == share.key.id()).get()
                    if gift.status == SharedGift.READY:
                        gift.deactivate_cup(client)
                    response['branch_name'] = share_data.get('name')
                    response['branch_phone'] = share_data.get('phone')

    return response


class RegistrationHandler(ApiHandler):
    def post(self):
        response = perform_registration(self.request)
        self.render_json(response)
