# -*- coding: utf-8 -*-

__author__ = 'dvpermyakov'

from base import ApiHandler


class GetSharedInfo(ApiHandler):
    def get(self):
        app_url_template = "http://dblb.mobi/get/%s%s"
        ua = self.request.headers["User-Agent"]
        platform_part = "a" if "Android" in ua else "i"
        client_id = self.request.get("client_id")
        client_id_part = "" if not client_id else ("/" + client_id)

        self.render_json({
            'image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image.png',
            'fb_android_image_url': 'http://empatika-doubleb-test.appspot.com/images/facebook_shared_image.png',
            'text_share_new_order': "Я эксперт кофе 80-го уровня",
            'text_share_about_app': "Советую попробовать это интересное приложение для заказа кофе в 3 клика:",
            'app_url': app_url_template % (platform_part, client_id_part),
            'screen_title': 'Ого! Поздравляю!\nНапиток в подарок от Mastercard!',
            'screen_text': 'Расскажи друзьям, если тебе нравится приложение Даблби.\nЕсть, что улучшить? Тогда напиши нам!'
        })
