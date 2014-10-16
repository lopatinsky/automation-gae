from webapp2_extras import jinja2
from methods import fastcounter
from handlers import api, web_admin
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
        PathPrefixRoute('/admin', [
            Route('/cancel.php', api.CancelOrderHandler),
            Route('/done.php', api.DoneOrderHandler),
            Route('/postpone.php', api.PostponeOrderHandler),
        ]),
        Route('/venues.php', api.VenuesHandler),
        Route('/menu.php', api.MenuHandler),
        Route('/order.php', api.OrderHandler),
        Route('/order_register.php', api.RegisterOrderHandler),
        Route('/status.php', api.StatusHandler),
        Route('/return.php', api.ReturnOrderHandler)
    ]),

    PathPrefixRoute('/admin', [
        Route('/orders.php', web_admin.OrdersHandler),
        Route('/backs.php', web_admin.ReturnsHandler),
        Route('/history.php', web_admin.HistoryHandler),

        Route('/check_time.php', web_admin.CheckTimeHandler),
        Route('/check_update.php', web_admin.CheckUpdateHandler),
        Route('/done.php', web_admin.OrderDoneHandler),
        Route('/return_barista.php', web_admin.OrderCancelHandler),
        Route('/status_up.php', web_admin.OrderStatusUpdateHandler)
    ]),

    Route('/task/counter_persist_incr', fastcounter.CounterPersistIncr),
], debug=True)

jinja2.set_jinja2(jinja2.Jinja2(app), app=app)
