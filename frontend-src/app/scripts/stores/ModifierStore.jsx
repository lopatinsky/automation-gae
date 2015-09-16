import BaseStore from './BaseStore';
import Actions from '../Actions';

const ModifierStore = new BaseStore({

    getModifier() {
        return this.modifier;
    },

    _setModifier(modifier) {
        this.modifier = modifier;
    }

}, action => {
    switch (action.actionType) {
        case Actions.INIT:
            if (action.data.request == "modifier") {
                ModifierStore._setModifier(action.data.item);
            }
            break;
    }
});

export default ModifierStore;