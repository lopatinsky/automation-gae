from handlers.api.user.admin.base import AdminApiHandler
from methods.auth import api_admin_required
from models.user import Courier

__author__ = 'dvpermyakov'


class CourierListHandler(AdminApiHandler):
    @api_admin_required
    def get(self):
        self.render_json({
            'couriers': [courier.dict() for courier in Courier.query(Courier.admin == self.user.key).fetch()]
        })