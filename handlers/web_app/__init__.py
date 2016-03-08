from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2
from models.config.config import config


class WebAppHandler(RequestHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        rendered = self.jinja2.render_template(template_name, **values)
        self.response.write(rendered)

    def get(self):
        if not config:
            self.abort(404)
        primary_color = None
        if config.APP_APPEARANCE_ANDROID and config.APP_APPEARANCE_ANDROID.toolbar_color != 'FF000000':
            primary_color = config.APP_APPEARANCE_ANDROID.toolbar_color
        elif config.ACTION_COLOR and config.ACTION_COLOR != 'FF000000':
            primary_color = config.ACTION_COLOR
        if not primary_color:
            primary_color = 'FFf44336'
        self.render('/app/index.html',
                    primary_color=primary_color,
                    namespace=config.key.namespace(),
                    title=config.APP_NAME)
