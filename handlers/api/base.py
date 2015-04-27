import json
import logging
import webapp2


class ApiHandler(webapp2.RequestHandler):
    def dispatch(self):
        for key, value in self.request.POST.iteritems():
            if key == "password":
                value = "(VALUE HIDDEN)"
            logging.debug("%s: %s" % (key, value))

        return_value = super(ApiHandler, self).dispatch()
        if self.response.status_int == 400 and "iOS/7.0.4" in self.request.headers["User-Agent"]:
            self.response.set_status(406)
        return return_value

    def abort(self, code, *args, **kwargs):
        if code == 400 and "iOS/7.0.4" in self.request.headers["User-Agent"]:
            code = 406
        super(ApiHandler, self).abort(code, *args, **kwargs)

    def render_json(self, obj):
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps(obj, separators=(',', ':')))
