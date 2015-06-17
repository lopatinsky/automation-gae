from handlers.api.user.courier.base import CourierBaseHandler

__author__ = 'dvpermyakov'


class InfoHandler(CourierBaseHandler):
    def get(self):
        self.render_json({
            'courier': self.user.dict(),
            'admin': self.user.admin.get().dict() if self.user.admin else None
        })