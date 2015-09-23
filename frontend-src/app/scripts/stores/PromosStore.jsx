import BaseStore from './BaseStore';
import Actions from '../Actions';

const PromosStore = new BaseStore({
    promos: [],

    getPromos() {
        return this.promos;
    },

    _setPromos(promos) {
        this.promos = promos;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "promos") {
                PromosStore._setPromos(action.data.promos);
            }
            break;
        case Actions.AJAX_FAILURE:
            alert('failure');
            break;
    }
});

export default PromosStore;