from models.config.config import config

__author__ = 'dvpermyakov'


def get_menu_navigation_dict():
    if config.NAVIGATION:
        window = config.NAVIGATION.get_menu_window()
        return {
            "title": window.title,
            "text": window.text,
            "kind": window.kind
        }
    else:
        return []
