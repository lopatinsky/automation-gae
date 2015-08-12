from models.proxy.resto import RestoCompany, RestoClient
from requests import post_resto_register

__author__ = 'dvpermyakov'


def resto_registration(client):
    resto_company = RestoCompany.get()
    resto_client = RestoClient.get(client)
    resto_response = post_resto_register(resto_company, resto_client)
    if not resto_client:
        resto_client = RestoClient(client=client.key)
    resto_client.resto_customer_id = resto_response['customer_id']
    resto_client.put()
