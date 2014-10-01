from handlers import api
from webapp2 import Route, WSGIApplication
from webapp2_extras.routes import PathPrefixRoute


app = WSGIApplication([
    PathPrefixRoute('/api', [
        PathPrefixRoute('/payment', [
            Route('/unbind.php', api.UnbindCardHandler),
            Route('/register.php', api.PaymentRegisterHandler),
            Route('/status.php', api.PaymentStatusHandler),
            Route('/payment_binding.php', api.PaymentBindingHandler),
            Route('/reverse.php', api.PaymentReverseHandler)
        ])
    ])
], debug=True)
