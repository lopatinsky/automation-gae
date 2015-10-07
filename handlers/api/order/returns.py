# coding=utf-8
from datetime import datetime, timedelta
import logging
from google.appengine.api.namespace_manager import namespace_manager
from handlers.api.base import ApiHandler
from methods.orders.cancel import cancel_order
from models import Order
from models.config.config import config
from models.order import NEW_ORDER, CANCELED_BY_CLIENT_ORDER, CONFUSED_CHOICES, CONFUSED_OTHER

__author__ = 'dvpermyakov'


class ReturnOrderHandler(ApiHandler):
    def post(self):
        order_id = int(self.request.get('order_id'))
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(400)
        elif order.status != NEW_ORDER:
            self.response.status_int = 412
            self.render_json({
                'error': 1,
                'description': u'Заказ уже выдан или отменен'
            })
        else:
            now = datetime.utcnow()
            if now - order.date_created < timedelta(seconds=config.CANCEL_ALLOWED_WITHIN) or \
                    order.delivery_time - now > timedelta(minutes=config.CANCEL_ALLOWED_BEFORE):
                success = cancel_order(order, CANCELED_BY_CLIENT_ORDER, namespace_manager.get_namespace())
                if success:
                    reason_id = self.request.get('reason_id')
                    if reason_id:
                        reason_id = int(reason_id)
                        if reason_id in CONFUSED_CHOICES:
                            order.cancel_reason = reason_id
                        if reason_id == CONFUSED_OTHER:
                            order.cancel_reason_text = self.request.get('reason_text')
                        order.put()
                    self.render_json({
                        'error': 0,
                        'order_id': order.key.id()
                    })
                    logging.info(u'заказ %d отменен' % order_id)
                else:
                    self.response.status_int = 422
                    self.render_json({
                        'error': 1,
                        'description': u'При отмене возникла ошибка'  # todo: change this text
                    })
            else:
                self.response.status_int = 412
                self.render_json({
                    'error': 1,
                    'description': u'Отмена заказа невозможна, так как до его исполнения осталось менее %s минут.' %
                                   config.CANCEL_ALLOWED_BEFORE
                })
