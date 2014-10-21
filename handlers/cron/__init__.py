import webapp2
from close_orders import CloseOpenedOrdersHandler

__author__ = 'ilyazorin'


app = webapp2.WSGIApplication([('/cron/close_orders', CloseOpenedOrdersHandler),
                              ],
                              debug=True)