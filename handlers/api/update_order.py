__author__ = 'dvpermyakov'


from base import ApiHandler
from models import Order, OrderPositionDetails


class UpdateOrderPromos(ApiHandler):
    def post(self):

        json = {'orders': []}
        for order in Order.query().fetch():
            total_sum = 0
            items = []
            richest = None
            for item in order.items:
                item = item.get()
                total_sum += item.price
                items.append({
                    'name': item.title,
                    'price': item.price
                })
                if richest:
                    if richest.price < item.price:
                        richest = item
                else:
                    richest = item
            is_include = False
            if total_sum != order.total_sum:
                if not order.promos:
                    is_include = True
                    order.promos.append('master')
                    order_details = OrderPositionDetails(
                        item=richest.key,
                        price=richest.price / 2,
                        revenue=richest.price,
                        promos=['master']
                    )
                    order.item_details.append(order_details)
                    need_set_promo = True
                    for item in order.items:
                        item = item.get()
                        if item.key.id() != richest.key.id() or (not need_set_promo and item.key.id() == richest.key.id()):
                            order_details = OrderPositionDetails(
                                item=item.key,
                                price=item.price,
                                revenue=item.price,
                                promos=[]
                            )
                            order.item_details.append(order_details)
                        else:
                            if item.key.id() == richest.key.id():
                                need_set_promo = False
            else:
                if not order.item_details:
                    is_include = True
                    for item in order.items:
                        item = item.get()
                        order_details = OrderPositionDetails(
                            item=item.key,
                            price=item.price,
                            revenue=item.price,
                            promos=[]
                        )
                        order.item_details.append(order_details)
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
                'sum of items price': total_sum,
                'items': items,
                'promos': order.promos,
                'details': item_details
            }
            if is_include:
                json['orders'].append(params)
        self.render_json(json)