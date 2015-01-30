__author__ = 'dvpermyakov'


from base import ApiHandler
from models import Order, OrderPositionDetails


class UpdateOrderPromos(ApiHandler):
    def post(self):

        json = {'orders': []}
        for order in Order.query().fetch():
            if order.item_details:
                continue
            total = 0
            for item_key in order.items:
                item = item_key.get()
                order.item_details.append(OrderPositionDetails(
                    item=item_key,
                    price=item.price,
                    revenue=item.price,
                    promos=[]
                ))
                total += item.price
            if total != order.total_sum:
                order.promos = ['master']

                most_expensive = None
                for item in order.item_details:
                    if not most_expensive or item.price > most_expensive.price:
                        most_expensive = item
                item.price /= 2
                item.promos = ['master']
            order.put()

            item_details = []
            for item in order.item_details:
                item_details.append({
                    'price': item.price,
                    'revenue': item.revenue,
                    'promo': item.promos,
                    'item': item.item.get().title
                })
            params = {
                'order_id': order.key.id(),
                'total_sum_order': order.total_sum,
                'sum of items price': total,
                'promos': order.promos,
                'details': item_details
            }
            json['orders'].append(params)
        self.render_json(json)
