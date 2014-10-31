import webapp2
from close_orders import CloseOpenedOrdersHandler
from check_pings import CheckPingsHandler

__author__ = 'ilyazorin'


app = webapp2.WSGIApplication([
    ('/cron/close_orders', CloseOpenedOrdersHandler),
    ('/cron/check_pings', CheckPingsHandler),
], debug=True)
