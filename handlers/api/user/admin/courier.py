from handlers.api.user.admin.base import AdminApiHandler
from models.user import Courier

__author__ = 'dvpermyakov'


class CourierListHandler(AdminApiHandler):
    def get(self):
        couriers = Courier.query(Courier.admin == self.user.key).fetch()