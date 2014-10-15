import json
import webapp2


class AdminApiHandler(webapp2.RequestHandler):
    def render_json(self, obj):
        # content type not set intentionally
        self.response.write(json.dumps(obj, separators=(',', ':')))
