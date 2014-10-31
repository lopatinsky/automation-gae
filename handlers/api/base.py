import json
import logging
import webapp2


class ApiHandler(webapp2.RequestHandler):
    def dispatch(self):
        for key, value in self.request.POST.iteritems():
            if key != "password":
                logging.debug("%s: %s" % (key, value))
        return super(ApiHandler, self).dispatch()

    def render_json(self, obj):
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps(obj, separators=(',', ':')))
