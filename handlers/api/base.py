import json
import logging
from urlparse import urlparse
import decimal
from google.appengine.api.namespace_manager import namespace_manager
from webapp2 import cached_property, RequestHandler
from webapp2_extras import jinja2
from models.proxy.unified_app import AutomationCompany
from config import Config, PRODUCTION_HOSTNAME, DEMO_HOSTNAME
from webapp2_extras import auth


class SuperJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        super(SuperJSONEncoder, self).default(o)

    def _replace(self, o):
        if isinstance(o, float):
            s = "%.8f" % o
            return decimal.Decimal(s)
        elif isinstance(o, dict):
            return {k: self._replace(v) for k, v in o.iteritems()}
        elif isinstance(o, (list, tuple)):
            return map(self._replace, o)
        else:
            return o

    def encode(self, o):
        return super(SuperJSONEncoder, self).encode(self._replace(o))


class ApiHandler(RequestHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def dispatch(self):
        for key, value in self.request.POST.iteritems():
            if key == "password":
                value = "(VALUE HIDDEN)"
            logging.debug("%s: %s" % (key, value))
        self.request.init_namespace = None
        if PRODUCTION_HOSTNAME in urlparse(self.request.url).hostname:
            config = Config.get()
            if not config:
                self.abort(423)
            logging.debug('initial namespace=%s' % namespace_manager.get_namespace())
            namespace = self.request.headers.get('Namespace')
            if namespace:
                proxy_company = AutomationCompany.query(AutomationCompany.namespace == namespace).get()
                if proxy_company:
                    self.request.init_namespace = namespace_manager.get_namespace()
                    namespace_manager.set_namespace(namespace)
        elif urlparse(self.request.url).hostname == DEMO_HOSTNAME:
            if not namespace_manager.get_namespace():
                namespace = self.request.headers.get('Namespace')
                namespace_manager.set_namespace(namespace)
                config = Config.get()
                if not config:
                    self.abort(403)
        logging.debug('namespace=%s' % namespace_manager.get_namespace())
        return_value = super(ApiHandler, self).dispatch()
        if self.response.status_int == 400 and "iOS/7.0.4" in self.request.headers["User-Agent"]:
            self.response.set_status(406)
        return return_value

    @cached_property
    def auth(self):
        return auth.get_auth(request=self.request)

    def abort(self, code, *args, **kwargs):
        if code == 400 and "iOS/7.0.4" in self.request.headers["User-Agent"]:
            code = 406
        super(ApiHandler, self).abort(code, *args, **kwargs)

    def render_json(self, obj):
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps(obj, separators=(',', ':'), cls=SuperJSONEncoder))

    def render_doc(self, template_name, **values):
        rendered = self.jinja2.render_template('/docs/' + template_name, **values)
        self.response.write(rendered)
