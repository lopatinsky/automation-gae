import webapp2
from close_orders import CloseOpenedOrdersHandler
from check_pings import CheckPingsHandler
from handlers.cron.alfa_errors import CheckAlfaErrorsHandler
from handlers.cron.backup import LoadDataHandler
from handlers.cron.build_square_table import BuildSquareTableHandler
from handlers.cron.reporting import ReportSendHandler
from inactive_clients import InactiveUsersNotificationHandler
from clear_pings import ClearPingsHandler
from creating_orders import CheckCreatingOrdersHandler
from cancel_gifts import CancelGiftsHandler
from images import ResizeImageHandler
from geo_push import CloseGeoPushesHandler
from subsciption import CloseSubscriptionHandler
from resto_update import UpdateRestoHandler
from update_hit import UpdateRatingHandler, UpdateHitCategoryHandler
from promo import UpdatePromosHandler

__author__ = 'ilyazorin'


app = webapp2.WSGIApplication([
    ('/cron/close_orders', CloseOpenedOrdersHandler),
    ('/cron/check_pings', CheckPingsHandler),
    ('/cron/alfa_errors', CheckAlfaErrorsHandler),
    ('/cron/inactive_notify', InactiveUsersNotificationHandler),
    ('/cron/clear_pings', ClearPingsHandler),
    ('/cron/build_square_table', BuildSquareTableHandler),
    ('/cron/creating_orders', CheckCreatingOrdersHandler),
    ('/cron/resize_image', ResizeImageHandler),
    ('/cron/cancel_gifts', CancelGiftsHandler),
    ('/cron/send_reports', ReportSendHandler),
    ('/cron/subscription', CloseSubscriptionHandler),
    ('/cron/geo_push', CloseGeoPushesHandler),
    ('/cron/update_resto', UpdateRestoHandler),
    ('/cron/update_rating', UpdateRatingHandler),
    ('/cron/update_hit', UpdateHitCategoryHandler),
    ('/cron/update_promos', UpdatePromosHandler),
    ('/cron/load_backup', LoadDataHandler),
], debug=True)
