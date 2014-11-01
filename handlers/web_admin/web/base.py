from webapp2 import cached_property
from webapp2_extras import jinja2
from handlers.web_admin.auth_base import AuthBaseHandler


class BaseHandler(AuthBaseHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        values.update(admin=self.user)
        rendered = self.jinja2.render_template(template_name, **values)
        self.response.write(rendered)
