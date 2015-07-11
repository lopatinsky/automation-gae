from ..base import BaseHandler


class DemoWizardHandler(BaseHandler):
    def get(self):
        self.render('/demo/index.html')
