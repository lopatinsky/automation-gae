from datetime import timedelta

from google.appengine.api import namespace_manager
from lxml import etree
from lxml.builder import E

from handlers.ext_api.base import ExtBaseHandler
from models.client import Client
from models.config.config import config
from models.order import Order
from models.payment_types import CASH_PAYMENT_TYPE, CARD_COURIER_PAYMENT_TYPE, CARD_PAYMENT_TYPE
from models.venue import Venue


BITRIX_PAYMENT_TYPES = {
    CASH_PAYMENT_TYPE: 'cash',
    CARD_PAYMENT_TYPE: 'card_online',
    CARD_COURIER_PAYMENT_TYPE: 'card_courier',
}


class BitrixBaseHandler(ExtBaseHandler):
    def check_auth(self):
        namespace = self.request.route_kwargs['namespace']
        namespace_manager.set_namespace(namespace)
        if not config \
                or not config.BITRIX_EXT_API_MODULE \
                or not config.BITRIX_EXT_API_MODULE.status:
            return False
        return True


class BitrixOrderInfoHandler(BitrixBaseHandler):
    @staticmethod
    def _personal_data(order):
        client = Client.get(order.client_id)
        change = None
        if config.ORDER_MODULE \
                and config.ORDER_MODULE.status \
                and config.ORDER_MODULE.enable_change \
                and order.payment_type_id == CASH_PAYMENT_TYPE:
            change = order.extra_data['cash_change']
        if not change:
            change = '0'
        payment_method = BITRIX_PAYMENT_TYPES[order.payment_type_id]
        return E.personal_data(
            E.name("%s %s" % (client.name, client.surname)),
            E.phone_code(client.tel[1:4]),
            E.phone(client.tel[4:]),
            E.city(order.address.city),
            E.address(order.address.str()),
            E.subway(),
            E.street(order.address.street),
            E.building(order.address.home),
            E.block(),
            E.apt(order.address.flat),
            E.entrance(),
            E.floor(),
            E.doorcode(),
            E.change(change),
            E.payment_method(payment_method),
            E.is_corporate('0')
        )

    @staticmethod
    def _cart(order):
        item_dicts = Order.grouped_item_dict(order.item_details)
        products = [
            E.product(id=item_dict['id'],
                      title=item_dict['title'],
                      quantity=str(item_dict['quantity']),
                      price="%.2f" % item_dict['price'])
            for item_dict in item_dicts
            ]
        return E.cart(*products)

    def get(self, namespace, order_id):
        order_id = int(order_id)
        order = Order.get_by_id(order_id)
        if not order:
            self.abort(404)
        venue = Venue.get(order.venue_id)
        order_created_local = order.date_created + timedelta(hours=venue.timezone_offset)
        xml = E.order(
            self._personal_data(order),
            E.order_details(
                E.is_delivery_asap('0'),
                E.delivery_time(order.delivery_time_str)
            ),
            self._cart(order),
            date_n_time=order_created_local.strftime("%Y-%m-%d %H:%M:%S"),
            total="%.2f" % order.total_sum,
            id="%s/%s" % (namespace, order_id),
        )
        self.response.content_type = 'application/xml;charset=utf-8'
        self.response.write(etree.tostring(xml))
