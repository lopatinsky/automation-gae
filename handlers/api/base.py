import json
import logging
from google.appengine.api.namespace_manager import namespace_manager
import webapp2
from webapp2_extras import jinja2
from models.proxy.unified_app import AutomationCompany
from config import Config


class ApiHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def dispatch(self):
        for key, value in self.request.POST.iteritems():
            if key == "password":
                value = "(VALUE HIDDEN)"
            logging.debug("%s: %s" % (key, value))
        config = Config.get()
        if not config:
            self.abort(434)
        logging.debug('initial namespace=%s' % namespace_manager.get_namespace())
        namespace = self.request.headers.get('Namespace')
        self.request.init_namespace = None
        if namespace:
            proxy_company = AutomationCompany.query(AutomationCompany.namespace == namespace).get()
            if proxy_company:
                self.request.init_namespace = namespace_manager.get_namespace()
                namespace_manager.set_namespace(namespace)
        logging.debug('namespace=%s' % namespace_manager.get_namespace())
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

    def render_doc(self, template_name, **values):
        rendered = self.jinja2.render_template('/docs/' + template_name, **values)
        self.response.write(rendered)