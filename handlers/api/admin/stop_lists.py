# coding:utf-8
from base import AdminApiHandler
import json
from methods.auth import api_user_required
from models import MenuItem, STATUS_AVAILABLE


class SetStopListHandler(AdminApiHandler):
    def send_error(self, description):
        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': description
        })

    @api_user_required
    def post(self):
        venue = None
        if self.user.venue:
            venue = self.user.venue.get()
        if not venue:
            self.send_error('Не связки с точкой кофейни')
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
        venue.put()
        self.render_json({
            'success': True
        })