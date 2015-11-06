import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';
import settings from '../settings';

const MenuStore = new BaseStore({
    previousCategories: [],
    categories: [],

    _removeSelected() {
        var categories = this.getCategories();
        for (var i = 0; i < categories.length; i++) {
            categories[i].selected = false;
        }
    },

    getCategory(category_id) {
        for (var i = 0; i < this.categories.length; i++) {
            if (category_id == this.categories[i].info.category_id) {
                return this.categories[i];
            }
        }
    },

    setSelected(category_id) {
        this._removeSelected();
        var category = this.getCategory(category_id);
        category.selected = true;
        this._changed();
    },

    getSelected() {
        var categories = this.getCategories();
        for (var i = 0; i < categories.length; i++) {
            if (categories[i].selected == true) {
                return categories[i].info.category_id;
            }
        }
        return null;
    },

    getSelectedIndex() {
        var selected = this.getSelected();
        for (var i = 0; i < this.categories.length; i++) {
            if (this.categories[i].info.category_id == selected) {
                return i;
            }
        }
        return 0;
    },

    getItem(category_id, item_id) {
        var category = this.getCategory(category_id);
        if (category == null) {
            return null;
        }
        for (var i = 0; i < category.items.length; i++) {
            if (item_id == category.items[i].id) {
                return category.items[i];
            }
        }
    },

    getCategories() {
        return this.categories;
    },

    getItems(category) {
        for (var i = 0; i < this.categories.length; i++) {
            if (category.info.category_id == this.categories[i].info.category_id) {
                return this.categories[i].items;
            }
        }
    },

    nextCategories(categories) {
        this.previousCategories.push(this.categories);
        this.categories = categories;
        this._changed();
    },

    canUndoCategories() {
        return this.previousCategories.length > 0;
    },

    undoCategories() {
        this._removeSelected();
        if (this.previousCategories.length > 0) {
            this.categories = this.previousCategories.pop();
        }
        this._changed();
    },

    __sort_categories(categories) {
        categories.sort(function(first, second) {
            return first.info.order - second.info.order;
        });
        for (var i = 0; i < categories.length; i++) {
            this.__sort_categories(categories[i].categories);
            categories[i].items.sort(function(first, second) {
                return first.order - second.order;
            });
        }
    },

    __getPicture(category) {
        var i;
        var pic;
        if (category.categories.length > 0) {
            console.log('in getting cats');
            var categories = category.categories;
            for (i = 0; i < categories.length; i++) {
                if (categories[i].info.pic) {
                    return categories[i].info.pic;
                }
                pic = this.__getPicture(categories[i]);
                if (pic) {
                    return pic;
                }
            }
        } else {
            console.log('in getting items');
            var items = category.items;
            for (i = 0; i < items.length; i++) {
                if (items[i].pic) {
                    return items[i].pic;
                }
            }
        }
        return settings.defaultCategoryPic;
    },

    _saveMenu(menu) {
        this.categories = menu;
        this.__sort_categories(this.categories);
        for (var i = 0; i < this.categories.length; i++) {
            var category = this.categories[i];
            if (!category.info.pic) {
                console.log(this.__getPicture(category));
                category.info.pic = this.__getPicture(category);
            }
        }
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "menu") {
                MenuStore._saveMenu(action.data.menu);
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            break;
    }
});

export default MenuStore;
