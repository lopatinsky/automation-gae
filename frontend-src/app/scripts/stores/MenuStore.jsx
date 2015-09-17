import BaseStore from './BaseStore';
import Actions from '../Actions';

const MenuStore = new BaseStore({
    previousCategories: [],
    categories: null,

    getCategory(category_id) {
        for (var i = 0; i < this.categories.length; i++) {
            if (category_id == this.categories[i].info.category_id) {
                return this.categories[i];
            }
        }
    },

    getItem(category_id, item_id) {
        var category = this.getCategory(category_id);
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

    _saveMenu(menu) {
        this.categories = menu;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "menu") {
                MenuStore._saveMenu(action.data.menu);
            }
            break;
        case Actions.AJAX_FAILURE:
            alert('failure');
            break;
    }
});

export default MenuStore;
