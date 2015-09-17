import BaseStore from './BaseStore';
import Actions from '../Actions';

const OrderStore = new BaseStore({
    total_sum: 0,
    items: [],

    getTotalSum() {
        return this.total_sum;
    },

    getItems() {
        return this.items;
    },

    addItem(item, total_sum) {
        this.items.push(item);
        this.total_sum += total_sum;
        this._changed();
    }

}, action => {
    switch (action.actionType) {

    }
});

export default OrderStore;
