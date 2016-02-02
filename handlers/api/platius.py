# coding=utf-8
from webapp2 import uri_for

from methods import platius
from models.client import Client
from models.platius import PlatiusClient
from .base import ApiHandler


def _get_barcode_info(platius_client):
    barcode_info = platius.get_user_bar_code(platius_client)
    barcode_num = barcode_info["barCode"]
    return {
        "authorized": True,
        "barcode_info": {
            "image_url": uri_for("platius_barcode", code=barcode_num, _full=True),
            "expires_in": barcode_info["ttlSeconds"],
        },
        "payment_code": str(barcode_num)[1:]
    }


class PlatiusStatusHandler(ApiHandler):
    def get(self):
        client_id = int(self.request.headers['Client-Id'] or 0)
        if not client_id:
            self.abort(400)
        client = Client.get(client_id)
        if not client_id:
            self.abort(400)

        platius_client, valid = PlatiusClient.get_and_validate(client)
        if not valid:
            self.render_json({
                "authorized": False
            })
            return

        self.render_json(_get_barcode_info(platius_client))


class PlatiusBarcodeImageHandler(ApiHandler):
    def get(self):
        code = self.request.get('code')

        self.response.content_type = 'image/png'
        code_image = platius.generate_bar_code(code)
        code_image.write(self.response, {
            'quiet_zone': 0,
            'font_size': 0,
            'text_distance': 0,
        })


class PlatiusSendSmsHandler(ApiHandler):
    def post(self):
        client_id = int(self.request.headers['Client-Id'] or 0)
        if not client_id:
            self.abort(400)
        client = Client.get(client_id)
        if not client_id:
            self.abort(400)

        try:
            platius.send_sms(client.tel)
        except platius.PlatiusError:
            self.render_json({
                "success": False,
                "description": u'Ошибка при отправке сообщения. Проверьте Ваш номер телефона и попробуйте еще раз'
            })
        else:
            self.render_json({
                "success": True,
                "description": u"СМС-подтверждение успешно отправлено на номер %s" % client.tel
            })


class PlatiusCheckSmsCodeHandler(ApiHandler):
    def post(self):
        client_id = int(self.request.headers['Client-Id'] or 0)
        if not client_id:
            self.abort(400)
        client = Client.get(client_id)
        if not client_id:
            self.abort(400)

        code = self.request.get('code')
        try:
            check_result = platius.check_sms(client.tel, code)
        except platius.PlatiusError:
            self.render_json({
                "authorized": False
            })
        else:
            platius_client = PlatiusClient.create_or_overwrite(client, check_result['userId'], check_result['token'])
            self.render_json(_get_barcode_info(platius_client))
