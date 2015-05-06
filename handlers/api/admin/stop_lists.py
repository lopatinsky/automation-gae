# coding:utf-8
import logging
from urlparse import urlparse
from base import AdminApiHandler
import json
from methods.auth import api_user_required
from models import MenuItem, STATUS_AVAILABLE, SingleModifier, GroupModifierChoice, GroupModifier


class MenuHandler(AdminApiHandler):
    def get(self):
        venue = self.venue_or_error
        logging.info(venue)
        url = u'http://%s.1.%s/api/menu?venue_id=%s&dynamic' % (self.user.namespace,
                                                                urlparse(self.request.url).hostname, venue.key.id())
        self.redirect(str(url))


class ModifiersHandler(AdminApiHandler):
    def get(self):
        venue = self.venue_or_error
        url = u'http://%s.1.%s/api/modifiers?venue_id=%s' % (self.user.namespace, urlparse(self.request.url).hostname,
                                                             venue.key.id())
        self.redirect(str(url))


class DynamicInfoHandler(AdminApiHandler):
    def get(self):
        venue = self.venue_or_error
        url = u'http://%s.1.%s/api/dynamic_info?venue_id=%s' % (self.user.namespace,
                                                                urlparse(self.request.url).hostname, venue.key.id())
        self.redirect(str(url))


class SetStopListHandler(AdminApiHandler):
    @api_user_required
    def post(self):
        venue = self.venue_or_error
        stop_list = json.loads(self.request.get('stop_list'))
        for item_id in stop_list.get('stopped'):
            item = MenuItem.get_by_id(int(item_id))
            if not item:
                return self.send_error(u'Продукт не найден')
            if item.status != STATUS_AVAILABLE:
                return self.send_error(u'Продукт %s не имеет статуса доступен' % item.title)
            if venue.key in item.restrictions:
                return self.send_error(u'Продукт %s недоступен в данном заведении' % item.title)
            if item.key in venue.stop_lists:
                return self.send_error(u'Продукт %s уже в стоп-листе' % item.title)
            venue.stop_lists.append(item.key)
        for item_id in stop_list.get('recovered'):
            item = MenuItem.get_by_id(int(item_id))
            if not item:
                return self.send_error(u'Продукт не найден')
            if item.status != STATUS_AVAILABLE:
                return self.send_error(u'Продукт %s не имеет статуса доступен' % item.title)
            if venue.key in item.restrictions:
                return self.send_error(u'Продукт %s недоступен в данном заведении' % item.title)
            if item.key not in venue.stop_lists:
                return self.send_error(u'Продукт %s не находится в стоп-листе' % item.title)
            venue.stop_lists.remove(item.key)
        for single_modifier_id in stop_list.get('stopped_single_modifiers'):
            item = SingleModifier.get_by_id(int(single_modifier_id))
            if not item:
                return self.send_error(u'Одиночный модификатор не найден')
            if item.key in venue.single_modifiers_stop_list:
                return self.send_error(u'Одиночный модификатор %s уже в стоп-листе' % item.title)
            venue.single_modifiers_stop_list.append(item.key)
        for single_modifier_id in stop_list.get('recovered_single_modifiers'):
            item = SingleModifier.get_by_id(int(single_modifier_id))
            if not item:
                return self.send_error(u'Одиночный модификатор не найден')
            if item.key not in venue.single_modifiers_stop_list:
                return self.send_error(u'Одиночный модификатор %s не находится в стоп-листе' % item.title)
            venue.single_modifiers_stop_list.remove(item.key)
        for group_choice_id in stop_list.get('stopped_group_choices'):
            item = GroupModifierChoice.query(GroupModifierChoice.choice_id == int(group_choice_id)).get()
            if not item:
                return self.send_error(u'Выбор группового модификатора не найден')
            if item.key in venue.group_choice_modifier_stop_list:
                return self.send_error(u'Выбор группового модификатора %s уже в стоп-листе' % item.title)
            venue.group_choice_modifier_stop_list.append(item.key)
        for group_choice_id in stop_list.get('recovered_group_choices'):
            item = GroupModifierChoice.query(GroupModifierChoice.choice_id == int(group_choice_id)).get()
            if not item:
                return self.send_error(u'Выбор группового модификатора не найден')
            if item.key not in venue.group_choice_modifier_stop_list:
                return self.send_error(u'Выбор группового модификатора %s не находится в стоп-листе' % item.title)
            venue.group_choice_modifier_stop_list.remove(item.key)

        for group_choice_id_with_item_id in stop_list.get('stopped_group_choices_with_item_id'):
            group_choice_id = int(group_choice_id_with_item_id.get('choice_id'))
            item_id = group_choice_id_with_item_id.get('item_id')
            modifier = GroupModifier.get_modifier_by_choice(group_choice_id)
            item = MenuItem.get_by_id(int(item_id))
            if not modifier:
                return self.send_error(u'Выбор группового модификатора не найден')
            if not item:
                return self.send_error(u"Продукт не найден")
            if modifier.key not in item.group_modifiers:
                return self.send_error(u"Продукт не связан с этим групповым модификатором")
            if group_choice_id in item.stop_list_group_choices:
                return self.send_error(u'Выбор группового модификатора %s уже в стоп-листе' % item.title)
            item.stop_list_group_choices.append(group_choice_id)
            item.put()
        for group_choice_id_with_item_id in stop_list.get('recovered_group_choices_with_item_id'):
            group_choice_id = int(group_choice_id_with_item_id.get('choice_id'))
            item_id = group_choice_id_with_item_id.get('item_id')
            modifier = GroupModifier.get_modifier_by_choice(group_choice_id)
            item = MenuItem.get_by_id(int(item_id))
            if not modifier:
                return self.send_error(u'Выбор группового модификатора не найден')
            if not item:
                return self.send_error(u"Продукт не найден")
            if modifier.key not in item.group_modifiers:
                return self.send_error(u"Продукт не связан с этим групповым модификатором")
            if group_choice_id not in item.stop_list_group_choices:
                return self.send_error(u'Выбор группового модификатора %s не в стоп-листе' % item.title)
            item.stop_list_group_choices.remove(group_choice_id)
            item.put()
        venue.put()
        self.render_json({
            'success': True
        })