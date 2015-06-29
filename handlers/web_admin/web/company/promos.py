# coding:utf-8
from config import config, Config
from methods.auth import company_user_required
from models import Promo, PromoCondition, PromoOutcome, STATUS_AVAILABLE, STATUS_UNAVAILABLE, MenuCategory, MenuItem, GiftMenuItem
from base import CompanyBaseHandler
from models.promo import CONDITION_MAP, OUTCOME_MAP
from models.venue import DELIVERY_MAP

__author__ = 'dvpermyakov'

CONDITION = 0
OUTCOME = 1
FEATURES_TYPES = [CONDITION, OUTCOME]


class PromoListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promos = Promo.query().fetch()
        for promo in promos:
            for condition in promo.conditions:
                condition.value_string = str(condition.value) if condition.value else ""
                if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
                    condition.value_string = DELIVERY_MAP[condition.value]
                elif condition.method == PromoCondition.CHECK_HAPPY_HOURS:
                    condition.additional_info = '(%s;%s)' % (condition.hh_days, condition.hh_hours)
        self.render('/promos/list.html', **{
            'promo_api_key': config.PROMOS_API_KEY if config.PROMOS_API_KEY else '',
            'wallet_api_key': config.WALLET_API_KEY if config.WALLET_API_KEY else '',
            'promos': promos,
            'condition_map': CONDITION_MAP,
            'outcome_map': OUTCOME_MAP
        })

    @company_user_required
    def post(self):
        for promo in Promo.query().fetch():
            confirmed = bool(self.request.get(str(promo.key.id())))
            if confirmed:
                promo.status = STATUS_AVAILABLE
            else:
                promo.status = STATUS_UNAVAILABLE
            promo.put()
        self.redirect('/company/main')


class ChangeApiKeysHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/promos/api_keys.html', **{
            'promo_api_key': config.PROMOS_API_KEY,
            'wallet_api_key': config.WALLET_API_KEY
        })

    @company_user_required
    def post(self):
        config = Config.get()
        config.PROMOS_API_KEY = self.request.get('promo_api_key')
        if not config.PROMOS_API_KEY:
            config.PROMOS_API_KEY = None
        config.WALLET_API_KEY = self.request.get('wallet_api_key')
        if not config.WALLET_API_KEY:
            config.WALLET_API_KEY = None
        config.put()
        self.redirect('/company/promos/list')


class AddPromoHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/promos/add.html')

    @company_user_required
    def post(self):
        promo = Promo()
        promo.title = self.request.get('name')
        promo.description = self.request.get('description')
        promo.put()
        self.redirect('/company/promos/list')


class ChooseMenuItemHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        feature_type = self.request.get_range('feature_type')
        if feature_type not in FEATURES_TYPES:
            self.abort(400)
        number = self.request.get_range('number')
        if feature_type == OUTCOME:
            if len(promo.outcomes) <= number:
                self.abort(400)
            feature = promo.outcomes[number]
            feature_name = OUTCOME_MAP[feature.method]
        elif feature_type == CONDITION:
            if len(promo.conditions) <= number:
                self.abort(400)
            feature = promo.conditions[number]
            feature_name = CONDITION_MAP[feature.method]
        else:
            feature_name = u'Не найдено'
            feature = None
        categories = MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()
        for category in categories:
            items = []
            for item in category.menu_items:
                item = item.get()
                item.has = False
                if item.status == STATUS_AVAILABLE:
                    if feature.item_required:
                        if item.key == feature.item:
                            item.has = True
                    items.append(item)
            category.items = items
        self.render('/promos/choose_product.html', **{
            'categories': categories,
            'promo': promo,
            'feature_name': feature_name,
            'feature_number': number,
        })

    @company_user_required
    def post(self):
        item_id = self.request.get('product_id')
        if item_id:
            item = MenuItem.get_by_id(int(item_id))
        else:
            item = None
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        feature_type = self.request.get_range('feature_type')
        if feature_type not in FEATURES_TYPES:
            self.abort(400)
        number = self.request.get_range('number')
        feature = None
        if feature_type == OUTCOME:
            if len(promo.outcomes) <= number:
                self.abort(400)
            feature = promo.outcomes[number]
        elif feature_type == CONDITION:
            if len(promo.conditions) <= number:
                self.abort(400)
            feature = promo.conditions[number]
        if item:
            feature.item = item.key
            feature.item_required = True
        else:
            feature.item_required = False
        promo.put()
        self.redirect('/company/promos/list')


class AddPromoConditionHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        methods = []
        for condition in PromoCondition.CHOICES:
            methods.append({
                'name': CONDITION_MAP[condition],
                'value': condition
            })
        self.render('/promos/add_condition_or_outcome.html', promo=promo, methods=methods, feature_condition=True)

    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        condition = PromoCondition()
        condition.method = self.request.get_range('method')
        condition.value = self.request.get_range('value')
        hh_days = self.request.get('hh_days')
        hh_hours = self.request.get('hh_hours')
        # todo: need validate days and hours
        if condition.method == PromoCondition.CHECK_HAPPY_HOURS and hh_days and hh_hours:
            condition.hh_days = hh_days
            condition.hh_hours = hh_hours
        promo.conditions.append(condition)
        promo.put()
        self.redirect('/company/promos/list')


class AddPromoOutcomeHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        methods = []
        for condition in PromoOutcome.CHOICES:
            methods.append({
                'name': OUTCOME_MAP[condition],
                'value': condition
            })
        self.render('/promos/add_condition_or_outcome.html', promo=promo, methods=methods)

    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        outcome = PromoOutcome()
        outcome.method = self.request.get_range('method')
        outcome.value = self.request.get_range('value')
        promo.outcomes.append(outcome)
        promo.put()
        self.redirect('/company/promos/list')


class ListGiftsHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        gifts = GiftMenuItem.query().fetch()
        for gift in gifts:
            gift.title = gift.item.get().title
        self.render('/promos/gift_list.html', gifts=gifts)

    @company_user_required
    def post(self):
        for gift in GiftMenuItem.query().fetch():
            confirmed = bool(self.request.get(str(gift.key.id())))
            if confirmed:
                gift.status = STATUS_AVAILABLE
            else:
                gift.status = STATUS_UNAVAILABLE
            gift.put()
        self.redirect('/company/promos/list')


class AddGiftHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        categories = MenuCategory.query().fetch()
        for category in categories:
            category.items = []
            for item in category.menu_items:
                category.items.append(item.get())
        self.render('/promos/gift_add.html', categories=categories)

    @company_user_required
    def post(self):
        for item in MenuItem.query().fetch():
            confirmed = bool(self.request.get(str(item.key.id())))
            if confirmed:
                gift = GiftMenuItem(id=item.key.id(), item=item.key)
                gift.promo_id = self.request.get_range('promo_id')
                gift.points = self.request.get_range('points')
                gift.put()
        self.redirect('/company/promos/gifts/list')