# coding=utf-8
import datetime
from .base import BaseHandler
from .formatting import format_order
from methods.auth import user_required
from models import CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER, Order


class ReturnsHandler(BaseHandler):
    @user_required
    def get(self):
        try:
            date = self.request.get('date')
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except (ValueError, TypeError):
            date = datetime.date.today()
        date = datetime.datetime.combine(date, datetime.time())
        next_date = date + datetime.timedelta(days=1)
        orders = self.user.query_orders(Order.return_datetime >= date, Order.return_datetime < next_date,
                                        Order.status.IN((CANCELED_BY_CLIENT_ORDER, CANCELED_BY_BARISTA_ORDER))).fetch()
        orders_data = []
        for order in orders:
            order_data = format_order(order)
            order_data['return_datetime'] = order.return_datetime.strftime("%Y-%m-%d %H:%M")
            if order.status == CANCELED_BY_CLIENT_ORDER:
                order_data['return_comment'] = u"отмена клиентом"
            elif order.status == CANCELED_BY_BARISTA_ORDER:
                order_data['return_comment'] = u"отмена баристой:" + order.return_comment
            orders_data.append(order_data)

        self.render('returns.html', orders=orders_data)
