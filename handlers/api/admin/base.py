import json
from ..base import ApiHandler


class AdminApiHandler(ApiHandler):
    def render_json(self, obj):
        # content type not set intentionally
        self.response.write(json.dumps(obj, separators=(',', ':')))
