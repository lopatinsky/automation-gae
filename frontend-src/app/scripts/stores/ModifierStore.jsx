import BaseStore from './BaseStore';
import Actions from '../Actions';

const ModifierStore = new BaseStore({

    getChoices() {
        return this.getModifier().choices;
    },

    getModifier() {
        return this.modifier;
    },

    _setModifier(modifier) {
        this.modifier = modifier;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case Actions.INIT:
            if (action.data.request == "modifier") {
                ModifierStore._setModifier(action.data.modifier);
            }
            break;
    }
});

export default ModifierStore;