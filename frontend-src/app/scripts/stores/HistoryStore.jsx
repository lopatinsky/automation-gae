import BaseStore from './BaseStore';
import Actions from '../Actions';

const HistoryStore = new BaseStore({
    orders: [],

    getOrders() {
        return this.orders;
    },

    _setOrders(orders) {
        this.orders = orders;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case Actions.INIT:
            if (action.data.request == "history") {
                HistoryStore._setOrders(action.data.orders);
            }
            break;
    }
});

export default HistoryStore;