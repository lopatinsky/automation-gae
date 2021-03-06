import json
import logging
from collections import defaultdict

from handlers.web_admin.web.company.base import CompanyBaseHandler
from methods import branch_io
from models.config.basket_notification import BasketNotificationModule
from models.config.config import Config

# from models.config.inactive_clients import NOT_TYPES_MAP, NOT_TYPES, NotificatingInactiveUsersModule
from models.config.field import OrderModule
from models.config.inactive_clients import NOTIFICATION_TYPES_MAP, CONDITIONS_MAP, InactiveNotificationModule, \
    WITH_CASHBACK, N_POINTS_LEFT
from models.config.order_message import OrderMessageModule, Condition
from models.config.share import ShareInvitationModule
from methods.auth import config_rights_required

__author__ = 'Artem'
from models.config import config


class ConfigMainHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        self.render('/config_settings/config_settings.html')

    def post(self):
        checked = self.request.get('reject_order_checkbox') is not ''
        conf = config.Config.get()
        conf.REJECT_IF_NOT_IN_ZONES = checked

        conf.put()
        self.redirect_to('config_main')


class GoogleAnalyticsApiKeysHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        self.render('/config_settings/google_analytics_api_keys.html')

    def post(self):
        ios_key = self.request.get('google_analytics_api_key_ios')
        android_key = self.request.get('google_analytics_api_key_android')

        conf = config.Config.get()

        conf.GOOGLE_ANALYTICS_API_KEY_IOS = ios_key
        conf.GOOGLE_ANALYTICS_API_KEY_ANDROID = android_key

        conf.put()
        self.redirect_to('config_google_analytics')
        pass


class SetupOrderMessageModuleHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        conf = config.Config.get()

        if not conf.ORDER_MESSAGE_MODULE:
            conf.ORDER_MESSAGE_MODULE = OrderMessageModule()
            conf.ORDER_MESSAGE_MODULE.status = 0

        cond = Condition.query(Condition.type == 0, Condition.status == 1).get()

        if not cond:
            cond = Condition()
            cond.type = 0
            cond.status = 1
            cond.put()

        conf.ORDER_MESSAGE_MODULE.condition = cond.key

        conf.put()

        self.render('/config_settings/order_message_module/order_message_module_setup.html')

    @config_rights_required
    def post(self):
        status = self.request.get('status') is not ''
        default_message = self.request.get('default_message')

        conf = config.Config.get()

        if not conf.ORDER_MESSAGE_MODULE:
            conf.ORDER_MESSAGE_MODULE = OrderMessageModule()

        order_message_module = conf.ORDER_MESSAGE_MODULE

        order_message_module.default_message = default_message
        order_message_module.status = status

        conf.put()

        message_for_delivery = self.request.get('message_for_delivery')
        message_for_pickup = self.request.get('message_for_pickup')

        cond = Condition.query(Condition.type == 0, Condition.status == 1).get()

        if not cond:
            cond = Condition()
            cond.type = 0
            cond.status = 1
            pass

        cond.set_messages(message_for_pickup, message_for_pickup, message_for_delivery, message_for_pickup)
        cond.put()

        order_message_module.condition = cond.key
        conf.put()

        self.redirect_to('order_message_module')


class SetInvitationModuleHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        conf = config.Config.get()
        if not conf.SHARE_INVITATION_MODULE:
            conf.SHARE_INVITATION_MODULE = ShareInvitationModule()
            conf.SHARE_INVITATION_MODULE.status = 0
        self.render('/config_settings/invitation_module_setup.html')

    @config_rights_required
    def post(self):
        status = self.request.get('status') is not ''
        # status = self.request.get_range('status', min_value=0, max_value=1, default=1)
        after_order = self.request.get('after_order') is not ''
        after_number_order = self.request.get_range('after_number_order', min_value=1, default=3)

        about_title = self.request.get('about_title')
        about_description = self.request.get('about_description')
        invitation_text = self.request.get('invitation_text')
        invitation_image = self.request.get('invitation_image')

        sender_accumulated_points = self.request.get_range('sender_accumulated_points', default=0)
        sender_wallet_points = self.request.get_range('sender_wallet_points', default=0)

        recipient_accumulated_points = self.request.get_range('recipient_accumulated_points', default=0)
        recipient_wallet_points = self.request.get_range('recipient_wallet_points', default=0)

        conf = config.Config.get()

        if not conf.SHARE_INVITATION_MODULE:
            conf.SHARE_INVITATION_MODULE = ShareInvitationModule()

        share_invitation_module = conf.SHARE_INVITATION_MODULE

        share_invitation_module.status = status
        share_invitation_module.after_order = after_order
        share_invitation_module.after_number_order = after_number_order
        share_invitation_module.about_title = about_title
        share_invitation_module.about_description = about_description
        share_invitation_module.invitation_text = invitation_text
        share_invitation_module.invitation_image = invitation_image
        share_invitation_module.sender_accumulated_points = sender_accumulated_points
        share_invitation_module.sender_wallet_points = sender_wallet_points
        share_invitation_module.recipient_accumulated_points = recipient_accumulated_points
        share_invitation_module.recipient_wallet_points = recipient_wallet_points

        conf.put()

        self.redirect_to('company_main')


class CreateBranchApiKeyHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        self.render('/config_settings/create_branch_api_key.html')

    @config_rights_required
    def post(self):
        button_type = self.request.get('set_key_button')
        conf = config.Config.get()

        if button_type == 'key_is_inputed':
            branch_key = self.request.get('branch_key')
            branch_secret = self.request.get('branch_secret')
            conf.BRANCH_API_KEY = branch_key
            conf.BRANCH_SECRET_KEY = branch_secret
            conf.put()

        elif button_type == 'key_is_generated':

            user_id = '99126033420124274'
            app_name = conf.APP_NAME
            email = 'mdburshteyn@gmail.com'
            dev_name = 'ru-beacon'

            logging.debug(u"user_id: {0}, app_name: {1}, dev_name: {2}, dev_email: {3}"
                          .format(user_id, app_name, dev_name, email))

            branch_key, branch_secret = branch_io.create_app_key(user_id=user_id,
                                                                 app_name=app_name,
                                                                 dev_name=dev_name,
                                                                 dev_email=email)
            conf.BRANCH_API_KEY = branch_key
            conf.BRANCH_SECRET_KEY = branch_secret
            conf.put()

        self.redirect_to('create_branch_api_key')


class BasketNotificationModuleHandler(CompanyBaseHandler):
    def get(self):
        self.render('/config_settings/basket_notification_module_setup.html')

    def post(self):
        status = bool(self.request.get('status'))
        header = self.request.get('header')
        text = self.request.get('text')
        inactivity_duration = self.request.get_range('inactivity_duration')
        days_since_order = self.request.get_range('days_since_order')

        cnf = Config.get()

        module = cnf.BASKET_NOTIFICATION_MODULE
        if not module:
            module = BasketNotificationModule()
            cnf.BASKET_NOTIFICATION_MODULE = module

        module.status = status
        module.header = header
        module.text = text
        module.inactivity_duration = inactivity_duration
        module.days_since_order = days_since_order

        cnf.put()
        self.redirect_to('config_main')


class NotificationModulesHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        types = []
        conditions = []

        for user_type in NOTIFICATION_TYPES_MAP:
            types.append({
                'name': NOTIFICATION_TYPES_MAP[user_type],
                'value': user_type
            })

            conditions.append({
                'name': CONDITIONS_MAP[user_type],
                'value': user_type
            })
        self.render('/config_settings/inactive_users_notifications/notification_modules.html',
                    types=types, conditions=conditions)


class AddNotificationModuleHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        types = []
        # conditions = []

        for user_type in NOTIFICATION_TYPES_MAP:
            types.append({
                'name': NOTIFICATION_TYPES_MAP[user_type],
                'value': user_type
            })

        self.render('/config_settings/inactive_users_notifications/add_notification_module.html',
                    types=types, conditions=json.dumps(CONDITIONS_MAP))

    @config_rights_required
    def post(self):
        conditions_num = self.request.get_range('conditions_num')
        conditions_dict = defaultdict()
        for i in range(1, conditions_num + 1):
            value = self.request.get('value_{0}'.format(i))
            text = self.request.get('text_{0}'.format(i))
            conditions_dict[value] = text

        conditions = dict(conditions_dict)

        header = self.request.get('header')

        client_type = self.request.get_range('client_type')

        status = self.request.get('status') is not ''
        should_push = self.request.get('should_push') is not ''
        should_sms = self.request.get('should_sms') is not ''
        sms_if_has_points = self.request.get('sms_if_has_points') is not ''
        sms_if_has_cashback = self.request.get('sms_if_has_cashback') is not ''

        needed_cashback = self.request.get_range('needed_cashback')
        needed_points_left = self.request.get_range('needed_points_left')

        module = InactiveNotificationModule()

        module.type = client_type
        module.conditions = conditions
        module.status = status
        module.should_push = should_push
        module.should_sms = should_sms
        module.sms_if_has_points = sms_if_has_points
        module.sms_if_has_cashback = sms_if_has_cashback
        module.header = header

        if needed_cashback >= 0:
            module.needed_cashback = needed_cashback
            module.type = WITH_CASHBACK
        if needed_points_left >= 0:
            module.type = N_POINTS_LEFT
            module.needed_points_left = needed_points_left

        conf = config.Config.get()

        conf.INACTIVE_NOTIFICATION_MODULE.append(module)
        conf.put()
        self.redirect_to('notification_modules_list')


class EditNotificationModuleHandler(CompanyBaseHandler):
    def get(self):
        types = []
        conf = config.Config.get()

        module_num = self.request.get_range('module_num')

        module = conf.INACTIVE_NOTIFICATION_MODULE[module_num]

        for user_type in NOTIFICATION_TYPES_MAP:
            types.append({
                'name': NOTIFICATION_TYPES_MAP[user_type],
                'value': user_type
            })

        self.render('/config_settings/inactive_users_notifications/edit_notification_module.html',
                    types=types, conditions=json.dumps(module.conditions), module=module)

    def post(self):
        module_idx = self.request.get_range('module_idx')

        conf = config.Config.get()
        module = conf.INACTIVE_NOTIFICATION_MODULE[module_idx]

        conditions_num = self.request.get_range('conditions_num')

        conditions_dict = defaultdict()
        for i in range(0, conditions_num):
            value = self.request.get('value_{0}'.format(i))
            text = self.request.get('text_{0}'.format(i))
            conditions_dict[value] = text

        conditions = dict(conditions_dict)

        header = self.request.get('header')

        client_type = self.request.get_range('client_type')

        status = self.request.get('status') is not ''
        should_push = self.request.get('should_push') is not ''
        should_sms = self.request.get('should_sms') is not ''
        sms_if_has_points = self.request.get('sms_if_has_points') is not ''
        sms_if_has_cashback = self.request.get('sms_if_has_cashback') is not ''

        needed_cashback = self.request.get_range('needed_cashback')
        needed_points_left = self.request.get_range('needed_points_left')

        module.type = client_type
        module.conditions = conditions
        module.status = status
        module.should_push = should_push
        module.should_sms = should_sms
        module.sms_if_has_points = sms_if_has_points
        module.sms_if_has_cashback = sms_if_has_cashback
        module.header = header

        if needed_cashback >= 0:
            module.needed_cashback = needed_cashback
            module.type = WITH_CASHBACK
        if needed_points_left >= 0:
            module.type = N_POINTS_LEFT
            module.needed_points_left = needed_points_left

        conf.put()

        self.redirect_to('notification_modules_list')


class DeleteNotificationModuleHandler(CompanyBaseHandler):
    @config_rights_required
    def post(self):
        module_num = self.request.get_range('module_num')

        conf = config.Config.get()
        conf.INACTIVE_NOTIFICATION_MODULE.pop(module_num)
        conf.put()

        self.redirect_to('notification_modules_list')


class OrderModuleSetupHandler(CompanyBaseHandler):
    @config_rights_required
    def get(self):
        conf = config.Config.get()
        if not conf.ORDER_MODULE:
            conf.ORDER_MODULE = OrderModule()
            conf.ORDER_MODULE.status = 0

        conf.put()

        self.render('/config_settings/order_module_setup.html')

    @config_rights_required
    def post(self):
        status = bool(self.request.get('status'))
        enable_number_of_people = bool(self.request.get('enable_number_of_people'))
        enable_change = bool(self.request.get('enable_change'))

        conf = config.Config.get()

        conf.ORDER_MODULE.status = status
        conf.ORDER_MODULE.enable_number_of_people = enable_number_of_people
        conf.ORDER_MODULE.enable_change = enable_change

        conf.put()

        self.redirect_to('company_main')

