import logging
from google.appengine.api.namespace_manager import namespace_manager
from handlers.api.base import ApiHandler
from models import MenuItem
from methods.images import ICON_SIZE, get_new_image_url


class ResizeImageHandler(ApiHandler):
    def get(self):
        namespace_manager.set_namespace('perchiniribaris')
        for item in MenuItem.query().fetch():
            if item.picture:
                if not item.icon:
                    try:
                        item.icon = get_new_image_url('MenuItemIcon', item.key.id(), url=item.picture, size=ICON_SIZE)
                        item.put()
                    except:
                        logging.warning('exception in resize image 128')
                if not item.cut_picture:
                    logging.info(item.title)
                    try:
                        item.cut_picture = get_new_image_url('MenuItem', item.key.id(), url=item.picture)
                        item.put()
                    except:
                        logging.warning('exception in resize image max size')
