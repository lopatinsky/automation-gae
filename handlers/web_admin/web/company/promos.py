# coding:utf-8
from datetime import datetime
import json
from config import config, Config
from methods.auth import company_user_required
from methods.rendering import STR_TIME_FORMAT
from models import Promo, PromoCondition, PromoOutcome, STATUS_AVAILABLE, STATUS_UNAVAILABLE, MenuCategory, MenuItem, GiftMenuItem, GroupModifier
from base import CompanyBaseHandler
from models.promo import CONDITION_MAP, OUTCOME_MAP, PromoMenuItem
from models.schedule import DaySchedule, Schedule
from models.venue import DELIVERY_MAP

__author__ = 'dvpermyakov'

CONDITION = 0
OUTCOME = 1
FEATURES_TYPES = (CONDITION, OUTCOME)


class PromoListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promos = Promo.query().order(-Promo.priority).fetch()
        for promo in promos:
            conditions = []
            for condition in promo.conditions[:]:
                if condition.item_details and condition.item_details.item:
                    choice_titles = []
                    for choice_id in condition.item_details.group_choice_ids:
                        choice = GroupModifier.get_modifier_by_choice(choice_id).get_choice_by_id(choice_id)
                        choice_titles.append(choice.title)
                    condition.item_details.title = condition.item_details.item.get().title
                    if choice_titles:
                        condition.item_details.title += u'(%s)' % u', '.join(choice_titles)
                condition.value_string = str(condition.value) if condition.value else ""
                if condition.method == PromoCondition.CHECK_TYPE_DELIVERY:
                    condition.value_string = DELIVERY_MAP[condition.value]
                    conditions.append(condition)
                elif condition.method in [PromoCondition.CHECK_HAPPY_HOURS, PromoCondition.CHECK_HAPPY_HOURS_CREATED_TIME]:
                    for day in (condition.schedule.days if condition.schedule else []):
                        new_condition = PromoCondition(method=condition.method)
                        new_condition.value_string = day.str()
                        conditions.append(new_condition)
                else:
                    conditions.append(condition)
            for outcome in promo.outcomes[:]:
                if outcome.item_details and outcome.item_details.item:
                    choice_titles = []
                    for choice_id in outcome.item_details.group_choice_ids:
                        choice = GroupModifier.get_modifier_by_choice(choice_id).get_choice_by_id(choice_id)
                        choice_titles.append(choice.title)
                    outcome.item_details.title = outcome.item_details.item.get().title
                    if choice_titles:
                        outcome.item_details.title += u'(%s)' % u', '.join(choice_titles)
            promo.conditions = conditions
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
            confirmed_status = bool(self.request.get('status_%s' % promo.key.id()))
            confirmed_visible = bool(self.request.get('visible_%s' % promo.key.id()))
            if not confirmed_status:
                confirmed_visible = False
            if confirmed_status:
                promo.status = STATUS_AVAILABLE
            else:
                promo.status = STATUS_UNAVAILABLE
            if confirmed_visible:
                promo.visible = STATUS_AVAILABLE
            else:
                promo.visible = STATUS_UNAVAILABLE
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
        promo.priority = Promo.generate_priority()
        promo.put()
        self.redirect('/company/promos/list')


class EditPromoHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        self.render('/promos/add.html', promo=promo)

    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
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
            for item in category.get_items(only_available=True):
                if item.key == feature.item_details.item:
                    item.has = True
                else:
                    item.has = False
                items.append(item)
            category.items = items
        self.render('/promos/choose_product.html', **{
            'categories': categories,
            'promo': promo,
            'feature': feature,
            'feature_name': feature_name,
            'feature_number': number,
        })

    @company_user_required
    def post(self):
        item_id = self.request.get('product_id')
        choice_ids = []
        if item_id:
            item = MenuItem.get_by_id(int(item_id))
            for modifier in item.group_modifiers:
                modifier = modifier.get()
                choice_id = self.request.get_range('modifier_%s_%s' % (item.key.id(), modifier.key.id()))
                if choice_id:
                    choice = modifier.get_choice_by_id(choice_id)
                    if choice:
                        choice_ids.append(choice_id)
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
            feature.item_details.item = item.key
            feature.item_details.group_choice_ids = choice_ids
        else:
            feature.item_details.item = None
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
            if condition == PromoCondition.CHECK_HAPPY_HOURS:
                continue
            methods.append({
                'name': CONDITION_MAP[condition],
                'value': condition
            })
        methods = sorted(methods, key=lambda method: method['name'])
        self.render('/promos/add_condition_or_outcome.html', promo=promo, methods=methods)

    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        condition = PromoCondition()
        condition.method = self.request.get_range('method')
        condition.value = self.request.get_range('value')
        condition.item_details = PromoMenuItem()
        promo.conditions.append(condition)
        promo.put()
        self.redirect('/company/promos/list')


class AddHappyHoursHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        days = []
        for day in DaySchedule.DAYS:
            days.append({
                'name': DaySchedule.DAY_MAP[day],
                'value': day,
                'exist': False,
                'start': '00:00',
                'end': '00:00'
            })
        methods = []
        for condition in PromoCondition.CHOICES:
            if condition in [PromoCondition.CHECK_HAPPY_HOURS, PromoCondition.CHECK_HAPPY_HOURS_CREATED_TIME]:
                methods.append({
                    'name': CONDITION_MAP[condition],
                    'value': condition
                })
        self.render('/schedule.html', **{
            'promo': promo,
            'days': days,
            'methods': methods
        })

    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        days = []
        for day in DaySchedule.DAYS:
            confirmed = bool(self.request.get(str(day)))
            if confirmed:
                start = datetime.strptime(self.request.get('start_%s' % day), STR_TIME_FORMAT)
                end = datetime.strptime(self.request.get('end_%s' % day), STR_TIME_FORMAT)
                days.append(DaySchedule(weekday=day, start=start.time(), end=end.time()))
        schedule = Schedule(days=days)
        condition = PromoCondition()
        condition.method = self.request.get_range('method')
        condition.schedule = schedule
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
        methods = sorted(methods, key=lambda method: method['name'])
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
        outcome.item_details = PromoMenuItem()
        promo.outcomes.append(outcome)
        promo.put()
        self.redirect('/company/promos/list')


class ListGiftsHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        gifts = GiftMenuItem.query().fetch()
        for gift in gifts:
            gift.title = gift.item.get().title
            choice_titles = []
            for choice_id in gift.additional_group_choice_restrictions:
                choice = GroupModifier.get_modifier_by_choice(choice_id).get_choice_by_id(choice_id)
                choice_titles.append(choice.title)
            if choice_titles:
                gift.title += u'(%s)' % u', '.join(choice_titles)
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
            for item in category.get_items():
                category.items.append(item)
        self.render('/promos/gift_add.html', categories=categories)

    @company_user_required
    def post(self):
        for item in MenuItem.query().fetch():
            confirmed = bool(self.request.get(str(item.key.id())))
            if confirmed:
                choice_ids = []
                for modifier in item.group_modifiers:
                    modifier = modifier.get()
                    choice_id = self.request.get_range('modifier_%s_%s' % (item.key.id(), modifier.key.id()))
                    if choice_id:
                        choice = modifier.get_choice_by_id(choice_id)
                        if choice:
                            choice_ids.append(choice_id)
                gift = GiftMenuItem(item=item.key)
                gift.promo_id = self.request.get_range('promo_id')
                gift.points = self.request.get_range('points')
                gift.additional_group_choice_restrictions = choice_ids
                gift.put()
        self.redirect('/company/promos/gifts/list')


class UpPromoHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        previous = promo.get_previous()
        if not previous:
            self.abort(400)
        number = previous.priority
        previous.priority = promo.priority
        promo.priority = number
        promo.put()
        previous.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'promo_id': promo.key.id(),
            'previous_id': previous.key.id()
        }, separators=(',', ':')))


class DownPromoHandler(CompanyBaseHandler):
    @company_user_required
    def post(self):
        promo_id = self.request.get_range('promo_id')
        promo = Promo.get_by_id(promo_id)
        if not promo:
            self.abort(400)
        next_ = promo.get_next()
        if not next_:
            self.abort(400)
        number = next_.priority
        next_.priority = promo.priority
        promo.priority = number
        promo.put()
        next_.put()
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps({
            'success': True,
            'promo_id': promo.key.id(),
            'next_id': next_.key.id()
        }, separators=(',', ':')))