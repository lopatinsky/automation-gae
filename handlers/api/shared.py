# -*- coding: utf-8 -*-

__author__ = 'dvpermyakov'

from base import ApiHandler


class GetSharedInfo(ApiHandler):
    def get(self):
        self.render_json({
            'image_url': 'http://empatika-doubleb-test.appspot.com/images/shared_image.png',
            'fb_android_image_url': 'http://empatika-doubleb-test.appspot.com/images/facebook_shared_image.png',
            'text_share_new_order': "Я эксперт кофе 80-го уровня",
            'text_share_about_app': "Советую попробовать это интересное приложение для заказа кофе в 3 клика:",
            'app_url': 'https://itunes.apple.com/app/id908237281',
            'screen_title': 'Ого! Поздравляю!\nНапиток в подарок от Mastercard!',
            'screen_text': 'Расскажи друзьям, если тебе нравится приложение Даблби.\nЕсть, что улучшить? Тогда напиши нам!'
        })