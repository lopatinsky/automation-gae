import logging
from handlers.api.base import ApiHandler
from models import MenuItem
from methods.images import MAX_SIZE, ICON_SIZE


class ResizeImageHandler(ApiHandler):
    def get(self):
        #namespace_manager.set_namespace('chikarabar')  todo: set namespace here
        for item in MenuItem.query().fetch():
            if item.picture:
                if not item.icon:
                    try:
                        pass
                        #resize_image(item, item.picture, ICON_SIZE, icon=True)
                    except:
                        logging.warning('exception in resize image 128')
                if not item.cut_picture:
                    try:
                        pass
                        #resize_image(item, item.picture, MAX_SIZE)
                    except:
                        logging.warning('exception in resize image max size')