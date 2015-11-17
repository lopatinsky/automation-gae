from handlers.api.base import ApiHandler
from methods.hit import include_hit_category
from models import MenuCategory, Venue


class MenuHandler(ApiHandler):
    def get(self):
        subscription_include = self.request.get('request_subscription') == 'true'
        menu_frame_include = self.request.get('request_menu_frame') == 'true'
        venue_id = self.request.get('venue_id')
        dynamic = "dynamic" in self.request.params
        venue = None
        city = self.request.city if self.request.city else None
        if venue_id:
            venue = Venue.get_by_id(int(venue_id))
            if not venue:
                self.abort(400)
        menu = MenuCategory.get_menu_dict(venue=venue, city=city,
                                          subscription_include=subscription_include,
                                          menu_frame_include=menu_frame_include)
        include_hit_category(menu)
        response = {
            "menu": menu,
            "dynamic": venue.dynamic_info() if venue and dynamic else None,
        }
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