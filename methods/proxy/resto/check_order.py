from config import Config
from requests import post_resto_check_order

__author__ = 'dvpermyakov'


def request_resto_check_order():
    config = Config.get()
    resto_company = config.RESTO_COMPANY.get()
    response = post_resto_check_order(resto_company)
