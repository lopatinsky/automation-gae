# -*- coding: utf-8 -*-
import random

__author__ = 'dvpermyakov'

from base import ApiHandler


TEXTS = [
    ("a", u"Заказываю кофе через приложение Даблби. Экспертам хорошего кофе каждая шестая кружка в подарок. Вот как "
          u"сейчас."),
    ("b", u"Кофе встроился в мой метаболизм. Если у тебя то же самое, скачай приложение Даблби и получай каждую "
          u"шестую доз... кружку в подарок"),
    ("c", u"Этот колумбийский кофе вштыривает как надо, бро. Скачай приложение Даблби и получай качественный кофе "
          u"в подарок"),
]
random.seed()


class GetSharedInfo(ApiHandler):
    def get(self):
        text_id, text = random.choice(TEXTS)

        url_template = "http://dblb.mobi/get/%%s%s%s"
        ua = self.request.headers["User-Agent"]
        platform_part = "a" if "Android" in ua else "i"
        client_id = self.request.get("client_id")
        client_id_part = "" if not client_id else ("/" + client_id)
        campaign_url_template = url_template % (platform_part, client_id_part)

        self.render_json({
            'image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image.png',
            'fb_android_image_url': 'http://empatika-doubleb-test.appspot.com/images/facebook_shared_image.png',
            'text_share_new_order': text,
            'text_share_about_app': "Советую попробовать это интересное приложение для заказа кофе в 3 клика:",
            'app_url': campaign_url_template % text_id,
            'about_url': campaign_url_template % 'd',
            'screen_title': text,
            'screen_text': 'Расскажи друзьям, если тебе нравится приложение Даблби.'
        })
