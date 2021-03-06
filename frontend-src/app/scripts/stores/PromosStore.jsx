import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const PromosStore = new BaseStore({
    promos: [],

    _setPromos(promos) {
        this.promos = promos;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "promos") {
                PromosStore._setPromos(action.data.promos);
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            break;
    }
});

export default PromosStore;