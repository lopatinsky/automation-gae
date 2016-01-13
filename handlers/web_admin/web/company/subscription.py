# coding=utf-8
import logging
from google.appengine.ext import db
from handlers.web_admin.web.company import CompanyBaseHandler
from methods.auth import config_rights_required
from models.config import config
from models.config.subscription import SubscriptionModule
from models.subscription import SubscriptionTariff

__author__ = 'Artem'


class AddSubscriptionTariffHandler(CompanyBaseHandler):
    def get(self):
        self.render('/subscription/add_tariff.html')

    def post(self):
        status = self.request.get('status') is not ''
        title = self.request.get('title')
        description = self.request.get('description')
        price = self.request.get_range('price')
        amount = self.request.get_range('amount')
        duration_seconds = self.request.get_range('duration_seconds')

        sub_tariff = SubscriptionTariff()
        sub_tariff.status = status
        sub_tariff.title = title
        sub_tariff.description = description
        sub_tariff.price = price
        sub_tariff.amount = amount
        sub_tariff.duration_seconds = duration_seconds

        sub_tariff.put()

        self.redirect_to('tariffs_list')

class ChangeTariffStatusHandler(CompanyBaseHandler):
    def post(self):
        tariff_id = self.request.get_range('tariff_id')
        tariff = SubscriptionTariff.get_by_id(tariff_id)
        logging.debug(self.request.get('status'))
        if self.request.get('status') is not '':
            tariff.status = 1
        else:
            tariff.status = 0
        tariff.put()


class ListSubscriptionTariffHandler(CompanyBaseHandler):
    def get(self):
        tariffs = SubscriptionTariff.query().fetch()
        self.render('/subscription/tariffs_list.html', tariffs=tariffs)


class EditSubscriptionTariffHandler(CompanyBaseHandler):
    def get(self):
        tariff_id = self.request.get_range('tariff_id')

        tariff = SubscriptionTariff.get_by_id(tariff_id)

        self.render('/subscription/add_tariff.html', tariff=tariff)

    def post(self):
        status = self.request.get('status') is not ''
        title = self.request.get('title')
        description = self.request.get('description')
        price = self.request.get_range('price')
        amount = self.request.get_range('amount')
        duration_seconds = self.request.get_range('duration_seconds')

        tariff_id = self.request.get_range('tariff_id')
        sub_tariff = SubscriptionTariff.get_by_id(tariff_id)

        sub_tariff.status = status
        sub_tariff.title = title
        sub_tariff.description = description
        sub_tariff.price = price
        sub_tariff.amount = amount
        sub_tariff.duration_seconds = duration_seconds

        sub_tariff.put()

        self.redirect_to('tariffs_list')


# class DeleteSubscriptionTariffHandler(CompanyBaseHandler):
#     def post(self):
#         tariff_id = self.request.get_range('tariff_id')
#         tariff = SubscriptionTariff.get_by_id(tariff_id)
#         tariff.key.delete()

class SubscriptionTariffSetupHandler(CompanyBaseHandler):
    def get(self):
        self.render('/subscription/subscription_tariff_setup.html')

    def post(self):
        status = self.request.get('status') is not ''
        title = self.request.get('title')
        description = self.request.get('description')
        price = self.request.get_range('price')
        amount = self.request.get_range('amount')
        duration_seconds = self.request.get_range('duration_seconds')

        sub_tariff = SubscriptionTariff.get()
        sub_tariff.status = status
        sub_tariff.title = title
        sub_tariff.description = description
        sub_tariff.price = price
        sub_tariff.amount = amount
        sub_tariff.duration_seconds = duration_seconds

        sub_tariff.put()

        self.redirect_to('subscription_main')


class SubscriptionModuleSetupHandler(CompanyBaseHandler):
    def get(self):
        self.render('/subscription/subscription_module_setup.html')

    @config_rights_required
    def post(self):
        status = self.request.get('status') is not ''
        menu_title = self.request.get('menu_title')
        menu_description = self.request.get('menu_description')
        screen_title = self.request.get('screen_title')
        screen_description = self.request.get('screen_description')

        conf = config.Config.get()
        if not conf.SUBSCRIPTION_MODULE:
            conf.SUBSCRIPTION_MODULE = SubscriptionModule()
        # Пылесос Генри
        conf.SUBSCRIPTION_MODULE.status = status
        conf.SUBSCRIPTION_MODULE.menu_title = menu_title
        conf.SUBSCRIPTION_MODULE.menu_description = menu_description
        conf.SUBSCRIPTION_MODULE.screen_title = screen_title
        conf.SUBSCRIPTION_MODULE.screen_description = screen_description
        conf.put()

        self.redirect_to('subscription_main')


class SubscriptionMain(CompanyBaseHandler):
    def get(self):
        self.render('/subscription/subscription_main.html')
