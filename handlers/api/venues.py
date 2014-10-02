from handlers.api.base import ApiHandler
from models import Venue

__author__ = 'ilyazorin'

class VenuesHandler(ApiHandler):

    def get(self):
        #TODO venues in distance order
        venues = Venue.query().fetch()
        self.render_json({'venues': [venue.dict() for venue in venues]})
