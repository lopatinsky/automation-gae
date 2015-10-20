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

    _setStatus(orderId, status) {
        var order = this.getOrder(orderId);
        order.status = status;
        this._changed();
    },

    _setOrders(orders) {
        this.orders = orders;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.INIT:
            if (action.data.request == "history") {
                HistoryStore._setOrders(action.data.orders);
            }
            break;
        case ServerRequests.CANCEL:
            if (action.data.request == "history") {
                HistoryStore._setStatus(action.data.order_id, 2);
            }
    }
});

export default HistoryStore;