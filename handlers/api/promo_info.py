from .base import ApiHandler
from config import config
from methods import empatika_promos
from models import Client


class PromoInfoHandler(ApiHandler):
    def get(self):
        client_id = int(self.request.get("client_id"))
        client = Client.get_by_id(client_id)
        bonus_points = empatika_promos.get_user_points(client_id)
        self.render_json({
            "promo_enabled": config.PROMO_ENABLED,
            "promo_mastercard_only": config.PROMO_MASTERCARD_ONLY,
            "points_per_cup": config.POINTS_PER_CUP,
            "has_mastercard_orders": client.has_mastercard_orders,
            "bonus_points": bonus_points
        })
