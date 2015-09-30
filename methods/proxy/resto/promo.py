from google.appengine.api import memcache
from models import Promo
from models.proxy.resto import RestoCompany
from requests import get_resto_promos

__author__ = 'dvpermyakov'


def get_promos():
    resto_company = RestoCompany.get()
    resto_promos = get_resto_promos(resto_company)
    promos = memcache.get('promos_%s' % resto_company.key.id())
    if not promos:
        promos = []
        for index, resto_promo in enumerate(resto_promos['promos']):
            promo = Promo(id=resto_promo['id'])
            promo.title = resto_promo['name']
            promo.description = resto_promo['description']
            promo.priority = index
            promos.append(promo)
        memcache.set('promos_%s' % resto_company.key.id(), promos, time=3600)
    return promos
