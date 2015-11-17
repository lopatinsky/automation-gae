from models.proxy.doubleb import DoublebCompany, DoublebClient

__author__ = 'dvpermyakov'


def doubleb_place_order(client):
    company = DoublebCompany.get()
    doubleb_client = DoublebClient.get(client)
