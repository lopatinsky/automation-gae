import json
import logging
from google.appengine.api import namespace_manager
from webapp2 import cached_property
from webapp2_extras import jinja2
from handlers.web_admin.auth_base import AuthBaseHandler
from methods import excel
from models import CompanyUser
from models.config.config import config


class CompanyBaseHandler(AuthBaseHandler):
    def dispatch(self):
        if self.user:
            if self.user.namespace:
                namespace_manager.set_namespace(self.user.namespace)
            elif self.session.get("namespace") is not None:
                namespace_manager.set_namespace(self.session["namespace"])
            elif self.request.route.name not in ("company_choose_namespace", "company_logout"):
                return self.redirect_to("company_choose_namespace")
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
        app_name = None
        if namespace_manager.get_namespace() is not None:
            app_name = config.APP_NAME
        values.update(user=self.user, _app_name=app_name)
        rendered = self.jinja2.render_template('/company' + template_name, **values)
        self.response.write(rendered)

    def render_report(self, report_name, values):
        values.update(padmin=self.user)  # todo: replace padmin to user
        if self.request.get("button") == "xls":
            excel.send_excel_file(self, report_name, report_name + '.html', **values)
        else:
            rendered = self.jinja2.render_template('/mt/reports/%s.html' % report_name, **values)
            self.response.write(rendered)
    
    @cached_property
    def user(self):
        current_namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace('')
        logging.info(self.request.cookies)
        user_dict = self.auth.get_user_by_session()
        namespace_manager.set_namespace(current_namespace)
        if user_dict is None:
            return None
        return CompanyUser.get_by_id(user_dict["user_id"])