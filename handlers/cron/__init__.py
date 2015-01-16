import webapp2
from close_orders import CloseOpenedOrdersHandler
from check_pings import CheckPingsHandler
from handlers.cron.alfa_errors import CheckAlfaErrorsHandler
from inactive_clients import FullyInactiveClientsHandler, SeveralDaysInactiveClientsHandler

__author__ = 'ilyazorin'


app = webapp2.WSGIApplication([
    ('/cron/close_orders', CloseOpenedOrdersHandler),
    ('/cron/check_pings', CheckPingsHandler),
    ('/cron/alfa_errors', CheckAlfaErrorsHandler),
    ('/cron/inactive_clients', FullyInactiveClientsHandler),
    ('/cron/weekly_inactive', SeveralDaysInactiveClientsHandler),
], debug=True)