import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const MenuStore = new BaseStore({
    previousCategories: [],
    categories: [],
    selected: null,

    getCategory(category_id) {
        for (var i = 0; i < this.categories.length; i++) {
            if (category_id == this.categories[i].info.category_id) {
                return this.categories[i];
            }
        }
    },

    setSelected(category_id) {
        this.selected = category_id;
        this._changed();
    },

    getSelected() {
        return this.selected;
    },

    getSelectedIndex() {
        for (var i = 0; i < this.categories.length; i++) {
            if (this.categories[i].info.category_id == this.selected) {
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

    _saveMenu(menu) {
        this.categories = menu;
        this.__sort_categories(this.categories);
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
            alert('failure');
            break;
    }
});

export default MenuStore;
