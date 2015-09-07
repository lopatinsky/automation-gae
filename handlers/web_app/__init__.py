from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2


class WebAppHandler(RequestHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        rendered = self.jinja2.render_template(template_name, **values)
        self.response.write(rendered)

    def get(self):
        self.render('/app/index.html')
