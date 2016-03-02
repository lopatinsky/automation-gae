# coding=utf-8
from methods.sms import sms_pilot
from models.config import config

_CONFIRMATION_TEXT = u"Ваш заказ №%s готовится, ожидайте доставку. %s"


def send_confirmation(order):
    conf = config.Config.get()

    phone = order.customer.get().phone
    sms_text = _CONFIRMATION_TEXT % (order.number, conf.APP_NAME)

    success, _ = sms_pilot.send_sms("INFORM", [phone[1:]], sms_text)
