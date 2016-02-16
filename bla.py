# coding=utf-8
from google.appengine.api import namespace_manager
from models.config.config import Config

__author__ = 'ivanoschepkov'


def run():
    namespace_manager.set_namespace('cosmotheca')
    config = Config.get()
    config.PLATIUS_WHITE_LABEL_MODULE.about_title = u'Разовый платежный код'
    config.PLATIUS_WHITE_LABEL_MODULE.about_description = u'Это Ваш разовый платежный код.\nПокажите его кассиру для того, чтобы пополнить ваш бонусный счет, или оплатить заказ'
    config.put()

