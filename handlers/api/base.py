import base64
import json
import logging

from webapp2 import cached_property, RequestHandler
from webapp2_extras import jinja2
from webapp2_extras import auth
from methods.client import save_city
from methods.rendering import log_params

from methods.versions import is_test_version, update_namespace
from models import Client, STATUS_AVAILABLE
from models.proxy.unified_app import ProxyCity, AutomationCompany


class FakeFloat(float):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return self._value


class SuperJSONEncoder(json.JSONEncoder):
    def _replace(self, o):
        if isinstance(o, float):
            return FakeFloat("%.8f" % o)
        elif isinstance(o, dict):
            return {k: self._replace(v) for k, v in o.iteritems()}
        elif isinstance(o, (list, tuple)):
            return map(self._replace, o)
        else:
            return o

    def encode(self, o):
        return super(SuperJSONEncoder, self).encode(self._replace(o))


class ApiHandler(RequestHandler):
    test = False

    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def dispatch(self):
        log_params(self.request.POST)
        logging.debug('Client-Id: %s' % self.request.headers.get('Client-Id'))
        version = int(self.request.headers.get('Version') or 0)
        logging.debug('Version: %s' % version)

        self.request.init_namespace = None
        namespace = self.request.headers.get('Namespace')
        success, init_namespace = update_namespace(namespace)
        if not success:
            self.abort(423)
        self.request.init_namespace = init_namespace

        self.test = is_test_version()

        client_id = self.request.headers.get('Client-Id')
        city_id = self.request.headers.get('City-Id')
        if city_id and client_id:
            company = AutomationCompany.query(AutomationCompany.status == STATUS_AVAILABLE).get()
            if company:
                city = ProxyCity.get_by_id(int(city_id))
            else:
                city = ProxyCity(city=base64.b64decode(city_id).decode('utf-8'))
            client = Client.get_by_id(int(client_id))
            if not city or not client_id:
                self.abort(400)
            self.request.city = city
            if company:
                save_city(client, city.key.id())
        else:
            self.request.city = None

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
