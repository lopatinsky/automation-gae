from handlers.api.base import ApiHandler
from models import MenuCategory, STATUS_AVAILABLE, Venue


def _get_menu(venue=None):
    return [category.dict(venue) for category in MenuCategory.query(MenuCategory.status == STATUS_AVAILABLE).fetch()]


class MenuHandler(ApiHandler):
    def get(self):
        venue_id = self.request.get('venue_id')
        venue = None
        if venue_id:
            venue = Venue.get_by_id(int(venue_id))
            if not venue:
                self.abort(400)
        self.render_json({
            "menu": _get_menu(venue) if venue else _get_menu()
        })