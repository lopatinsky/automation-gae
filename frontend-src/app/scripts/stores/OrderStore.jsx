import BaseStore from './BaseStore';
import Actions from '../Actions';

const OrderStore = new BaseStore({
    total_sum: 0,
    items: [],
    slot_id: null,

    getSlotId() {
        return this.slot_id;
    },

    getTotalSum() {
        return this.total_sum;
    },

    getItems() {
        return this.items;
    },

    setSlotId(slot_id) {
        this.slot_id = slot_id;
        this._changed();
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
