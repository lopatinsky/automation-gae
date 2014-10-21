import json
import logging
import webapp2


class ApiHandler(webapp2.RequestHandler):
    def dispatch(self):
        for item in self.request.POST.iteritems():
            logging.debug("%s: %s" % item)
        return super(ApiHandler, self).dispatch()

    def render_json(self, obj):
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps(obj, separators=(',', ':')))
