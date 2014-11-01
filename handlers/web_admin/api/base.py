import json
from handlers.web_admin.auth_base import AuthBaseHandler


class WebAdminApiHandler(AuthBaseHandler):
    def render_json(self, obj):
        # content type not set intentionally
        self.response.write(json.dumps(obj, separators=(',', ':')))
