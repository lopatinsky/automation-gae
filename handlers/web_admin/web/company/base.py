import json
import logging
from google.appengine.api import namespace_manager
from webapp2 import cached_property
from webapp2_extras import jinja2
from handlers.web_admin.auth_base import AuthBaseHandler
from models import CompanyUser


class CompanyBaseHandler(AuthBaseHandler):
    def dispatch(self):
        if self.user:
            namespace_manager.set_namespace(self.user.namespace)
        else:
            logging.info('user was not found')
            namespace_manager.set_namespace('')
        logging.debug('namespace=%s' % namespace_manager.get_namespace())
        super(CompanyBaseHandler, self).dispatch()

    def render_json(self, obj):
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps(obj, separators=(',', ':')))

    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        values.update(user=self.user)
        rendered = self.jinja2.render_template('/company' + template_name, **values)
        self.response.write(rendered)

    def report_render(self, template_name, **values):
        values.update(padmin=self.user)  # todo: replace padmin to user
        rendered = self.jinja2.render_template('/mt/reports' + template_name, **values)
        self.response.write(rendered)
    
    @cached_property
    def user(self):
        user_dict = self.auth.get_user_by_session()
        if user_dict is None:
            return None
        return CompanyUser.get_by_id(user_dict["user_id"])