from .base import ApiHandler
from models import Order, Client, SharedGift, Share
from models.order import CREATING_ORDER
from methods.branch_io import INVITATION
from models.share import SharedPromo


class HistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id'))
        history = Order.query(Order.client_id == client_id)
        sorted_history = sorted(history, key=lambda order: order.delivery_time, reverse=True)
        order_dicts = [order.history_dict() for order in sorted_history if order.status != CREATING_ORDER]
        self.render_json({
            'orders': order_dicts
        })


class SharedGiftHistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id'))
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        gifts = SharedGift.query(SharedGift.client_id == client_id).fetch()
        self.render_json({
            'gifts': [gift.dict() for gift in gifts]
        })


class SharedInvitationHistoryHandler(ApiHandler):
    def get(self):
        client_id = self.request.get_range('client_id') or int(self.request.headers.get('Client-Id'))
        client = Client.get_by_id(client_id)
        if not client:
            self.abort(400)
        shares = Share.query(Share.share_type == INVITATION, Share.sender == client.key).fetch()
        share_dicts = []
        for share in shares:
            share_dict = share.dict()
            shared_ready = 0
            shared_done = 0
            for shared_promo in SharedPromo.query(SharedPromo.sender == client.key).fetch():
                if shared_promo.status == SharedPromo.READY:
                    shared_ready += 1
                elif shared_promo.status == SharedPromo.DONE:
                    shared_done += 1
            share_dict.update({
                'ready_number': shared_ready,
                'done_number': shared_done
            })
            share_dicts.append(share_dict)
        self.render_json({
            'shares': share_dicts
        })