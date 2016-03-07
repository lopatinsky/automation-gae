import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

var STATUSES = {
    0: 'Новый',
    1: 'Готов',
    2: 'Отменен',
    3: 'Отменен',
    4: 'Подтвержден'
};


const HistoryStore = new BaseStore({
    loading: false,
    loadsCount: 0,
    orders: [],

    getOrders() {
        return this.orders;
    },

    getOrder(orderId) {
        var orders = this.getOrders();
        for (var i = 0; i < orders.length; i++) {
            if (orders[i].order_id == orderId) {
                return orders[i];
            }
        }
    },

    getStatus(status) {
        return STATUSES[status];
    },

    setLoading() {
        this.loading = true;
        this._changed();
    },

    unsetLoading() {
        this.loading = false;
        this._changed();
    },

    isLoading() {
        return this.loading;
    },

    isOrderLoaded() {
        return this.loadsCount > 0;
    },

    _setStatus(orderId, status) {
        var order = this.getOrder(orderId);
        order.status = status;
        this._changed();
    },

    _setOrders(orders) {
        this.orders = orders;
        this.loadsCount += 1;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "history") {
                HistoryStore._setOrders(action.data.orders);
                HistoryStore.unsetLoading();
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            if (action.data.request == "history") {
                HistoryStore.unsetLoading();
            }
            break;
        case ServerRequests.AJAX_SENDING:
            if (action.data.request == "history") {
                HistoryStore.setLoading();
            }
            break;
    }
});

export default HistoryStore;