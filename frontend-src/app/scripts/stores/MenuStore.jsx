import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';
import settings from '../settings';

const MenuStore = new BaseStore({
    rootCategories: [],
    categoriesById: {},
    itemsById: {},

    _clear() {
        this.rootCategories = [];
        this.categoriesById = {};
        this.itemsById = {};
    },

    _processOne(category) {
        this._process(category.categories);

        category.info.pic = this.__getPicture(category);
        category.items.sort(function(first, second) {
            return first.order - second.order;
        });

        this.categoriesById[category.info.category_id] = category;
        for (let item of category.items) {
            this.itemsById[item.id] = item;
        }
    },

    _process(categories) {
        categories.sort(function(first, second) {
            return first.info.order - second.info.order;
        });
        for (let cat of categories) {
            this._processOne(cat);
        }
    },

    __getPicture(category) {
        var i;
        var pic;
        if (category.categories.length > 0) {
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
        try {
            throw new Error();
        } catch (e) {}
        this._clear();
        this.rootCategories = menu;
        this._process(menu);
        this._changed();
    },

    getItemPrice(item, groupModifierChoices, singleModifierQuantities) {
        let price = item.price;
        for (let gm of item.group_modifiers) {
            const choice = groupModifierChoices[gm.modifier_id];
            if (choice != null) {
                price += choice.price;
            }
        }
        for (let sm of item.single_modifiers) {
            const quantity = singleModifierQuantities[sm.modifier_id];
            if (quantity) {
                price += sm.price * quantity;
            }
        }
        return price;
    },

    getDefaultModifiers(item) {
        let gmChoices = {}, smQuantities = {};
        for (let gm of item.group_modifiers) {
            gmChoices[gm.modifier_id] = this.getDefaultModifierChoice(gm);
        }
        for (let sm of item.single_modifiers) {
            smQuantities[sm.modifier_id] = 0;
        }
        return [gmChoices, smQuantities];
    },

    getDefaultItemPrice(item) {
        let [gmChoices, smQuantities] = getDefaultModifiers(item);
        return getItemPrice(item, gmChoices, smQuantities);
    },

    getDefaultModifierChoice(modifier) {
        if (!modifier.required) {
            return null;
        }
        for (var i = 0; i < modifier.choices.length; i++) {
            if (modifier.choices[i].default) {
                return modifier.choices[i];
            }
        }
        return modifier.choices[0];
    }
}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "menu") {
                MenuStore._saveMenu(action.data.menu);
            }
            break;
    }
});

export default MenuStore;
