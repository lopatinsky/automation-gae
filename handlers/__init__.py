import sys
from google.appengine.api import app_identity
from methods import email

_APP_ID = app_identity.get_application_id()


def handle_500(request, response, exception):
    body = """URL: %s
User-Agent: %s
Exception: %s
Logs: https://appengine.google.com/logs?app_id=s~%s&severity_level_override=0&severity_level=3""" \
           % (request.url, request.headers['User-Agent'], exception, _APP_ID)
    email.send_error("server_errors", "Error 500", body)

    exc_info = sys.exc_info()
    raise exc_info[0], exc_info[1], exc_info[2]
