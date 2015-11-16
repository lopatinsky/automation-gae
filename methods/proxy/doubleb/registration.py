from methods.proxy.doubleb.requests import post_doubleb_registration
from models.proxy.doubleb import DoublebCompany, DoublebClient

__author__ = 'dvpermyakov'


def doubleb_registration(client):
    company = DoublebCompany.get()
    doubleb_client = DoublebClient.get(client)
    response = post_doubleb_registration(company, doubleb_client)
    if not doubleb_client:
        doubleb_client = DoublebClient(id=response['client_id'], client=client.key)
        doubleb_client.put()