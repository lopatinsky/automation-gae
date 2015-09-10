import BaseStore from './BaseStore';
import Actions from '../Actions';

const MenuStore = new BaseStore({
    getCategories() {
        return this.categories;
    },

    getItems(category) {
        for (var i = 0; i < this.categories.length; i++) {
            if (category.category_id == this.categories[i].category_id) {
                return this.categories[i].items;
            }
        }
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "menu") {
                MenuStore.categories = action.data.menu;
            }
            break;
        case Actions.AJAX_FAILURE:
            alert('failure');
            break;
    }
});

export default MenuStore;
