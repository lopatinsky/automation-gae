from methods.proxy.doubleb.requests import post_doubleb_place_order
from models.proxy.doubleb import DoublebCompany, DoublebClient

__author__ = 'dvpermyakov'


def doubleb_place_order(order, client, venue, items, payment):
    company = DoublebCompany.get()
    doubleb_client = DoublebClient.get(client)
    response = post_doubleb_place_order(company, client, doubleb_client, venue, items, payment, order.delivery_time)
    return True, response
