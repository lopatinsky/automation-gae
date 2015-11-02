from handlers.api.user.admin.base import AdminApiHandler
from methods.proxy.resto.history import update_status
from models.config.config import config, RESTO_APP
from methods.auth import api_admin_required, write_access_required


class SyncRestoOrderHandler(AdminApiHandler):
    @api_admin_required
    @write_access_required
    def post(self, order_id):
        if config.APP_KIND != RESTO_APP:
            self.abort(400)
        order = self.user.order_by_id(int(order_id))
        update_status(order)  # todo maybe full sync sometime
        self.render_json({'order': order.dict(extra_fields_in_comment=self._is_android_barista_app)})
