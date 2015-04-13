# coding:utf-8
from base import AdminApiHandler
import json
from methods.auth import api_user_required
from models import MenuItem, STATUS_AVAILABLE, SingleModifier, GroupModifierChoice


class MenuHandler(AdminApiHandler):
    def get(self):
        venue = self.venue_or_error
        self.redirect('/api/menu.php?venue_id=%s&dynamic' % venue.key.id())


class ModifiersHandler(AdminApiHandler):
    def get(self):
        venue = self.venue_or_error
        self.redirect('/api/modifiers?venue_id=%s' % venue.key.id())


class DynamicInfoHandler(AdminApiHandler):
    def get(self):
        venue = self.venue_or_error
        self.redirect('/api/dynamic_info?venue_id=%s' % venue.key.id())


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
        venue.put()
        self.render_json({
            'success': True
        })