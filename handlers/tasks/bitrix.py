import logging
import re
import urllib

from google.appengine.api import namespace_manager, urlfetch, taskqueue
from webapp2 import RequestHandler

from methods.emails.admins import send_error
from models.config.config import config
from models.order import Order


class BitrixExportHandler(RequestHandler):
    def post(self):
        namespace = namespace_manager.get_namespace()
        order_id = self.request.get_range('order_id')
        logging.debug('Processing %s/%s', namespace, order_id)

        order = Order.get_by_id(order_id)
        if not order:
            logging.error('Not found order, aborting')
            return
        order_url = 'http://auto.rbcn.mobi' + self.uri_for('bitrix_order_info', namespace=namespace, order_id=order_id)

        bm = config.BITRIX_EXT_API_MODULE
        bitrix_params = {bm.param_name: order_url}
        bitrix_params.update(bm.constant_params)
        bitrix_url = "%s?%s" % (bm.url, urllib.urlencode(bitrix_params))
        logging.debug('Bitrix URL is %s', bitrix_url)

        try:
            result = urlfetch.fetch(bitrix_url, method='POST', deadline=60)
            if result.status_code >= 500:
                send_error('bitrix', 'Bitrix not responding when importing %s/%s' % (namespace, order_id), '')
                raise Exception('Bitrix fetch failed with status code %s' % result.status_code)
        except Exception as e:
            logging.exception(e)
            raise
        else:
            logging.debug(result.content)
            content = result.content.lower()
            if 'error' in content:
                logging.error('Error!')
                send_error('bitrix', 'Bitrix error when importing %s/%s' % (namespace, order_id), result.content)
            else:
                number_match = re.search('\d+', content)
                if number_match:
                    number = int(number_match.group())
                    logging.debug('Setting number to %s', number)
                    order.number = int(number)
                    order.put()
