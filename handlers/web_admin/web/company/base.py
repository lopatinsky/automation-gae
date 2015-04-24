from webapp2 import cached_property
from webapp2_extras import jinja2
from handlers.web_admin.auth_base import AuthBaseHandler
from models import CompanyUser


class BaseHandler(AuthBaseHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        values.update(admin=self.user)
        rendered = self.jinja2.render_template(template_name, **values)
        self.response.write(rendered)
    
    @cached_property
    def user(self):
        user_dict = self.auth.get_user_by_session()
        if user_dict is None:
            return None
        return CompanyUser.get_by_id(user_dict["user_id"])