__author__ = 'dvpermyakov'

from base import ApiHandler


class GetSharedInfo(ApiHandler):
    def get(self):
        self.render_json({
            'image_url': 'empatika-doubleb-test.appspot.com/images/shared_image.jpg',
            'text_share_new_order': "Я эксперт кофе 80-го уровня",
            'text_share_about_app': "Приложение Даблби позволяет легко и просто оформить и оплатить заказ без необходимости стоять в очереди",
            'app_url': 'https://itunes.apple.com/app/id908237281',
        })