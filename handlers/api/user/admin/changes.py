# coding=utf-8
from handlers.api.user.admin.base import AdminApiHandler
from methods.emails.admins import send_error
from methods.orders.cancel import cancel_order
from methods.orders.done import done_order
from methods.orders.postpone import postpone_order
from methods.orders.confirm import confirm_order
from methods.orders.courier import send_to_courier
from methods.auth import write_access_required, api_admin_required
from methods.rendering import timestamp
from models.order import CANCELED_BY_BARISTA_ORDER, CONFIRM_ORDER, NEW_ORDER
from models.user import Courier
from models.venue import DELIVERY, PICKUP

__author__ = 'ilyazorin'


class CancelOrderHandler(AdminApiHandler):
    @api_admin_required
    @write_access_required
    def post(self, order_id):
        comment = self.request.get('comment')
        order = self.user.order_by_id(int(order_id))
        success = cancel_order(order, CANCELED_BY_BARISTA_ORDER, self.user.namespace, comment=comment)
        if not success:
            self.response.status_int = 400
        self.render_json({})


class DoneOrderHandler(AdminApiHandler):
    def render_error(self, description):
        self.response.set_status(400)
        self.render_json({
            'success': True,
            'description': description
        })

    @api_admin_required
    @write_access_required
    def post(self, order_id):
        order = self.user.order_by_id(int(order_id))
        if order.status not in [NEW_ORDER, CONFIRM_ORDER]:
            self.abort(400)
        if order.status == NEW_ORDER and order.delivery_type in [DELIVERY, PICKUP]:
            return self.render_error(u'Необходимо сначала подтвердить заказ')
        try:
            done_order(order, self.user.namespace)
        except Exception as e:
            send_error('Close error', 'Barista error in closing order', str(e))
            return self.render_error(u'Непредвиденная ошибка! Повторите позднее! Не отменяйте заказ, если он уже оплачен!')
        self.render_json({
            "success": True,
            "delivery_time": timestamp(order.delivery_time),
            "actual_delivery_time": timestamp(order.actual_delivery_time)
        })


class PostponeOrderHandler(AdminApiHandler):
    @api_admin_required
    @write_access_required
    def post(self, order_id):
        mins = self.request.get_range("mins")
        order = self.user.order_by_id(int(order_id))
        postpone_order(order, mins, self.user.namespace)
        self.render_json({})


class ConfirmOrderHandler(AdminApiHandler):
    @api_admin_required
    @write_access_required
    def post(self, order_id):
        order = self.user.order_by_id(int(order_id))
        if order.status != NEW_ORDER:
            self.abort(400)
        confirm_order(order, self.user.namespace)
        self.render_json({})


class SendToCourierHandler(AdminApiHandler):
    @api_admin_required
    @write_access_required
    def post(self, order_id):
        courier_id = self.request.get_range('courier_id')
        courier = Courier.get_by_id(courier_id)
        if not courier:
            self.abort(400)
        order = self.user.order_by_id(int(order_id))
        if order.status != CONFIRM_ORDER:
            self.abort(400)
        send_to_courier(order, self.user.namespace, courier)
        self.render_json({})


class WrongVenueHandler(AdminApiHandler):
    @api_admin_required
    @write_access_required
    def post(self, order_id):
        order = self.user.order_by_id(int(order_id))
        if order.status != NEW_ORDER:
            self.abort(400)
        # todo: set code here
        self.render_json({})