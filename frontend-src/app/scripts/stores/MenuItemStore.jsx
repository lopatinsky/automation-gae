import BaseStore from './BaseStore';
import Actions from '../Actions';

const MenuItemStore = new BaseStore({

    getPrice() {
        var item = this.getItem();
        var price = item.price;
        var modifiers = this.getModifiers();
        for (var i = 0; i < modifiers.length; i++) {
            price += modifiers[i].chosen_choice.price;
        }
        modifiers = this.getSingleModifiers();
        for (i = 0; i < modifiers.length; i++) {
            price += modifiers[i].quantity * modifiers[i].price;
        }
        return price;
    },

    getItem() {
        return this.item;
    },

    getModifiers() {
        return this.item.group_modifiers;
    },

    getSingleModifiers() {
        return this.item.single_modifiers;
    },

    getSingleModifier(modifier_id) {
        var modifiers = this.getSingleModifiers();
        for (var i = 0; i < modifiers.length; i++) {
            if (modifier_id == modifiers[i].modifier_id) {
                return modifiers[i];
            }
        }
    },

    addSingleModifier(modifier_id) {
        var modifier = this.getSingleModifier(modifier_id);
        modifier.quantity += 1;
        this._changed();
    },

    deductSingleModifier(modifier_id) {
        var modifier = this.getSingleModifier(modifier_id);
        if (modifier.quantity > 0) {
            modifier.quantity -= 1;
        }
        this._changed();
    },

    getModifierChoices(modifier_id) {
        var modifiers = this.getModifiers();
        for (var i = 0; i < modifiers.length; i++) {
            if (modifier_id == modifiers[i].modifier_id) {
                return modifiers[i].choices;
            }
        }
    },

    setChoice(modifier, choice) {
        modifier.chosen_choice = choice;
        this._changed();
    },

    getDefaultModifierChoice(modifier) {
        for (var i = 0; i < modifier.choices.length; i++) {
            if (modifier.choices[i].default) {
                return modifier.choices[i];
            }
        }
    },

    _setItem(item) {
        this.item = item;
        for (var i = 0; i < item.group_modifiers.length; i++) {
            var modifier = item.group_modifiers[i];
            this.setChoice(modifier, this.getDefaultModifierChoice(modifier));
        }
        for (i = 0; i < item.single_modifiers.length; i++) {
            item.single_modifiers[i].quantity = 0;
        }
    }
}, action => {
    switch (action.actionType) {
        case Actions.INIT:
            if (action.data.request == "menu_item") {
                MenuItemStore._setItem(action.data.item);
            }
            break;
    }
});

export default MenuItemStore;