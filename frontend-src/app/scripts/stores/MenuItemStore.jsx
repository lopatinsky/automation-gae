import BaseStore from './BaseStore';

const MenuItemStore = new BaseStore({

    getItem() {
        return this.item;
    },

    getModifiers() {
        return this.item.group_modifiers;
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
    },

    _setItem(item) {
        this.item = item;
        for (var i = 0; i < item.group_modifiers.length; i++) {
            this.setChoice(item.group_modifiers[i], modifier.choices[0]);
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