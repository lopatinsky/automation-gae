from handlers.api.base import ApiHandler
from methods.navigation import get_menu_navigation_dict
from methods.subscription import get_subscription
from models import MenuCategory, Venue, Client
from models.specials import SubscriptionMenuItem, DayMenuItem


class MenuHandler(ApiHandler):
    def get(self):
        venue_id = self.request.get('venue_id')
        dynamic = "dynamic" in self.request.params
        venue = None
        if venue_id:
            venue = Venue.get_by_id(int(venue_id))
            if not venue:
                self.abort(400)
        response = {
            "menu": MenuCategory.get_menu_dict(venue),
            "dynamic": venue.dynamic_info() if venue and dynamic else None,
        }
        response.update({
            "navigation_window": get_menu_navigation_dict()
        })
        day_item = DayMenuItem.get()
        if day_item:
            response.update({
                "day_item": day_item.dict()
            })
        self.render_json(response)


class DynamicInfoHandler(ApiHandler):
    def get(self):
        venue_id = self.request.get_range('venue_id')
        venue = Venue.get_by_id(int(venue_id))
        if not venue:
            self.abort(400)
        self.render_json({
            'dynamic': venue.dynamic_info()
        })


class ModifiersHandler(ApiHandler):
    def get(self):

        venue_id = self.request.get('venue_id')
        venue = None
        if venue_id:
            venue = Venue.get_by_id(int(venue_id))
            if not venue:
                self.abort(400)
        single_modifiers = {}
        group_modifiers = {}
        for category in MenuCategory.query().fetch():
            for item in category.get_items():
                if venue and venue.key in item.restrictions:
                    continue
                for single_modifier in item.single_modifiers:
                    if single_modifier.id() not in single_modifiers:
                        single_modifiers[single_modifier.id()] = single_modifier.get()
                for group_modifier in item.group_modifiers:
                    if group_modifier.id() not in group_modifiers:
                        group_modifiers[group_modifier.id()] = group_modifier.get()

        self.render_json({
            'group_modifiers': [group_modifier.dict() for group_modifier in group_modifiers.values()],
            'single_modifiers': [single_modifier.dict() for single_modifier in single_modifiers.values()]
        })