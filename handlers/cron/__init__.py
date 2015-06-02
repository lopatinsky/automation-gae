import webapp2
from close_orders import CloseOpenedOrdersHandler
from check_pings import CheckPingsHandler
from handlers.cron.alfa_errors import CheckAlfaErrorsHandler
from handlers.cron.build_square_table import BuildSquareTableHandler
from inactive_clients import SeveralDaysInactiveClientsHandler, SuccessBindingCardHandler, BindingCardHandler
from clear_pings import ClearPingsHandler
from creating_orders import CheckCreatingOrdersHandler
from images import ResizeImageHandler

__author__ = 'ilyazorin'


app = webapp2.WSGIApplication([
    ('/cron/close_orders', CloseOpenedOrdersHandler),
    ('/cron/check_pings', CheckPingsHandler),
    ('/cron/alfa_errors', CheckAlfaErrorsHandler),
    ('/cron/sms_notify', SuccessBindingCardHandler),
    ('/cron/email_notify', BindingCardHandler),
    ('/cron/push_notify', SeveralDaysInactiveClientsHandler),
    ('/cron/clear_pings', ClearPingsHandler),
    ('/cron/build_square_table', BuildSquareTableHandler),
    ('/cron/creating_orders', CheckCreatingOrdersHandler),
    ('/cron/resize_image', ResizeImageHandler),
], debug=True)
