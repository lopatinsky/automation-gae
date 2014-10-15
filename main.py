from webapp2_extras import jinja2
from methods import fastcounter
from handlers import api, admin_api, admin_web
from webapp2 import Route, WSGIApplication
from webapp2_extras.routes import PathPrefixRoute


app = WSGIApplication([
    PathPrefixRoute('/api', [
        PathPrefixRoute('/payment', [
            Route('/unbind.php', api.UnbindCardHandler),
            Route('/register.php', api.PaymentRegisterHandler),
            Route('/status.php', api.PaymentStatusHandler),
            Route('/payment_binding.php', api.PaymentBindingHandler),
            Route('/reverse.php', api.PaymentReverseHandler),
            Route('/payment_types.php', api.PaymentTypesHandler),
        ]),
        Route('/venues.php', api.VenuesHandler),
        Route('/menu.php', api.MenuHandler),
        Route('/order.php', api.OrderHandler),
        Route('/order_register.php', api.RegisterOrderHandler),
        Route('/status.php', api.StatusHandler),
        Route('/return.php', api.ReturnOrderHandler)
    ]),

    PathPrefixRoute('/admin', [
        Route('/orders.php', admin_web.OrdersHandler),
        Route('/backs.php', admin_web.ReturnsHandler),
        Route('/history.php', admin_web.HistoryHandler),

        Route('/check_time.php', admin_api.CheckTimeHandler),
        Route('/check_update.php', admin_api.CheckUpdateHandler),
        Route('/done.php', admin_api.OrderDoneHandler),
        Route('/return_barista.php', admin_api.OrderCancelHandler),
        Route('/status_up.php', admin_api.OrderStatusUpdateHandler)
    ]),

    Route('/task/counter_persist_incr', fastcounter.CounterPersistIncr),
], debug=True)

jinja2.set_jinja2(jinja2.Jinja2(app), app=app)
