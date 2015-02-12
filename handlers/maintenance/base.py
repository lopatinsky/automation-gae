from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2, sessions, auth
from google.appengine.api import users


class BaseHandler(RequestHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        rendered = self.jinja2.render_template('mt/' + template_name, **values)
        self.response.write(rendered)

    @property
    def auth(self):
        return auth.get_auth(request=self.request)

    @cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @cached_property
    def session(self):
        return self.session_store.get_session()

    def dispatch(self):
        try:
            super(BaseHandler, self).dispatch()
        finally:
            self.session_store.save_sessions(self.response)