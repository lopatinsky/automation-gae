from google.appengine.api import memcache
from config import Config
from models import Promo
from requests import get_resto_promos

__author__ = 'dvpermyakov'


def get_promos():
    config = Config.get()
    resto_company = config.RESTO_COMPANY.get()
    resto_promos = get_resto_promos(resto_company)
    promos = memcache.get('promos_%s' % resto_company.key.id())
    if not promos:
        promos = []
        for resto_promo in resto_promos['promos']:
            promo = Promo(id=resto_promo['id'])
            promo.title = resto_promo['name']
            promo.description = resto_promo['description']
            promos.append(promo)
        memcache.set('promos_%s' % resto_company.key.id(), promos, time=3600)
    return promos
