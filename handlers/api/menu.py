import logging
from config import config
from handlers.api.base import ApiHandler
from models import MenuCategory, Client, STATUS_AVAILABLE, Share, SharedFreeCup, SharedGift, IOS_DEVICE, ANDROID_DEVICE
from methods import empatika_promos, versions
import json

__author__ = 'ilyazorin'


_FUCKUP_CLIENTS_MAP = {
    200053: 200500,
    200055: 200646,
    200056: 200252,
    200059: 200188,
}


class MenuHandler(ApiHandler):

    def get(self):
        client_id = self.request.get_range('client_id')
        if not client_id:
            first_enter = True
        else:
            first_enter = False

        old_version = not versions.supports_new_menu(self.request)

        device_phone = "".join(c for c in self.request.get('device_phone') if '0' <= c <= '9')
        categories = MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()
        result_dict = {}
        for category in categories:
            result_dict.update(category.dict(old_version))
        response = {'menu': result_dict}

        # fuckup iOS 1.1
        if client_id in _FUCKUP_CLIENTS_MAP:
            logging.warning("fuckup found: %s", client_id)
            client_id = _FUCKUP_CLIENTS_MAP[client_id]
        # fuckup end

        client = None
        try:
            client = Client.get_by_id(client_id)
        except:
            pass
        if not client and device_phone:
            client = Client.query(Client.device_phone == device_phone).get()

        if not client:
            client = Client.create()
            client.user_agent = self.request.headers["User-Agent"]
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
        response['demo'] = config.CARD_BINDING_REQUIRED

        share_date = self.request.get('share_data')

        if share_date:
            share_date = json.loads(share_date)
            share_id = share_date.get('share_id')
            if share_id:
                share = Share.get_by_id(share_id)
                if not share:
                    self.abort(400)
                if share.share_type == Share.INVITATION:
                    if first_enter:
                        SharedFreeCup(sender=share.sender, recipient=client.key).put()
                elif share.share_type == Share.GIFT:
                    if share.status == Share.ACTIVE:
                        gift = SharedGift.query(SharedGift.share_id == share.key.id()).get()
                        if not gift:
                            self.abort(400)
                        gift.activate_cup(client)

        self.render_json(response)
