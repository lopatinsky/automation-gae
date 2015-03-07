# coding=utf-8

import datetime
from .base import ApiHandler
from config import config
from methods import empatika_promos
from methods.rendering import timestamp
from models import Client, News


class PromoInfoHandler(ApiHandler):
    def get(self):
        client_id = int(self.request.get("client_id"))
        client = Client.get_by_id(client_id)
        bonus_points = empatika_promos.get_user_points(client_id)
        news = News.query(News.active == True).fetch()
        self.render_json({
            "geopush": {
                "id": str(datetime.date.today()),
                "send": config.DEBUG,
                "expires": 1424599097,
                "radius": config.GEOPUSH_SEND_RADIUS,
                "text": u"Тестовый геолокационный пуш."
            },

            "promo_enabled": config.PROMO_ENABLED,
            "promo_end_date": timestamp(config.PROMO_END_DATE),
            "promo_mastercard_only": config.PROMO_MASTERCARD_ONLY,
            "points_per_cup": config.POINTS_PER_CUP,
            "has_mastercard_orders": client.has_mastercard_orders,
            "bonus_points": bonus_points,
            "news": [n.dict() for n in news]
        })


class DemoInfoHandler(ApiHandler):
    def get(self):
        self.render_json({"demo": config.CARD_BINDING_REQUIRED})
