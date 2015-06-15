# coding:utf-8
from handlers.api.user.base import UserApiHandler


class AdminApiHandler(UserApiHandler):
    def send_error(self, description):
        self.response.set_status(400)
        self.render_json({
            'success': False,
            'description': description
        })

    @property
    def venue_or_error(self):
        venue = None
        if self.user.venue:
            venue = self.user.venue.get()
        if not venue:
            return self.send_error(u'Не связки с точкой кофейни')
        return venue