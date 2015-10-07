import sys

from models.config.config import Config
from methods.emails import admins
from models.config.version import CURRENT_APP_ID


def handle_500(request, response, exception):
    config = Config.get()
    if config and config.IN_PRODUCTION:
        body = """URL: %s
User-Agent: %s
Exception: %s
Logs: https://appengine.google.com/logs?app_id=s~%s&severity_level_override=0&severity_level=3""" \
                        % (request.url, request.headers['User-Agent'], exception, CURRENT_APP_ID)
        admins.send_error("server", "Error 500", body)
    exc_info = sys.exc_info()
    raise exc_info[0], exc_info[1], exc_info[2]
