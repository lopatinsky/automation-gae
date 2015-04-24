from datetime import datetime, timedelta
from base import AdminApiHandler
from methods.auth import api_user_required
from models import Order, READY_ORDER


class RevenueReportTodayHandler(AdminApiHandler):
    @api_user_required
    def get(self):
        venue_key = self.user.venue
        end = datetime.utcnow()
        start = end.replace(hour=0, minute=0)
        if venue_key:
            orders = Order.query(Order.date_created > start, Order.date_created < end,
                                 Order.venue_id == venue_key.id()).fetch()
        else:
            orders = Order.query(Order.date_created > start, Order.date_created < end).fetch()
        orders = [order for order in orders if order.status == READY_ORDER]
        self.render_json({
            'orders': len(orders),
            'revenue': sum(order.total_sum for order in orders)
        })


class RevenueReportMonthHandler(AdminApiHandler):
    def get_orders(self, start, end, venue_key):
        if venue_key:
            orders = Order.query(Order.date_created > start, Order.date_created < end,
                                 Order.venue_id == venue_key.id()).fetch()
        else:
            orders = Order.query(Order.date_created > start, Order.date_created < end).fetch()
        orders = [order for order in orders if order.status == READY_ORDER]
        return {
            'day': start.day,
            'orders': len(orders),
            'revenue': sum(order.total_sum for order in orders)
        }

    @api_user_required
    def get(self):
        venue_key = self.user.venue
        end = datetime.utcnow()
        start = end.replace(hour=0, minute=0, day=1)
        results = []
        while start < end:
            if start.day < end.day:
                start_end = start.replace(hour=0, minute=0, day=start.day+1)
                results.append(self.get_orders(start, start_end, venue_key))
            else:
                results.append(self.get_orders(start, end, venue_key))
            start += timedelta(days=1)
        self.render_json(results)