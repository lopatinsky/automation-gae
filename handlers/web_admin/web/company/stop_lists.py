from base import BaseHandler
from models import Venue, MenuItem, STATUS_AVAILABLE


class MainStopListHandler(BaseHandler):
    def get(self):
        venues = Venue.query().fetch()
        self.render('/stop_list/main.html', venues=venues)


class StopListsHandler(BaseHandler):
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        products = [product for product in MenuItem.query(MenuItem.status == STATUS_AVAILABLE).fetch()
                    if venue.key not in product.restrictions]
        for product in products:
            if product.key in venue.stop_lists:
                product.stopped = True
            else:
                product.stopped = False
        self.render('/stop_list/list.html', venue=venue, products=products)

    def post(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        products = [product for product in MenuItem.query(MenuItem.status == STATUS_AVAILABLE).fetch()
                    if venue.key not in product.restrictions]
        for product in products:
            stopped = not bool(self.request.get(str(product.key.id())))
            if stopped and product.key not in venue.stop_lists:
                venue.stop_lists.append(product.key)
                venue.put()
            if not stopped and product.key in venue.stop_lists:
                venue.stop_lists.remove(product.key)
                venue.put()
        self.redirect_to('main_stop_list')