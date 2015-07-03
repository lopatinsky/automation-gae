from handlers.api.user.courier.base import CourierBaseHandler
from methods.auth import api_courier_required

__author__ = 'dvpermyakov'


class InfoHandler(CourierBaseHandler):
    @api_courier_required
    def get(self):
        self.render_json({
            'courier': self.user.dict(),
            'admin': self.user.admin.get().dict() if self.user.admin else None
        })