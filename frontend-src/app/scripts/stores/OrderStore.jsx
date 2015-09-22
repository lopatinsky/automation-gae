import BaseStore from './BaseStore';
import Actions from '../Actions';

const OrderStore = new BaseStore({
    totalSum: 0,
    validationSum: 0,
    deliverySum: 0,
    deliverySumStr: '',
    items: [],
    slotId: null,
    promos: [],

    getSlotId() {
        return this.slotId;
    },

    getTotalSum() {
        return this.totalSum;
    },

    getItems() {
        return this.items;
    },

    getItemsDict() {
        return this.getItems().map(item => {
            return {
                quantity: 1,
                item_id: item.id,
                single_modifiers: [],
                group_modifiers: []
            }
        });
    },

    setSlotId(slotId) {
        this.slotId = slotId;
        this._changed();
    },

    addItem(item, totalSum) {
        this.items.push(item);
        this.totalSum += totalSum;
        this.validationSum = this.totalSum;
        this._changed();
    },

    getOrderDict() {
        return {
            delivery_type: '',
            client: '',
            device_type: 2,
            delivery_slot_id: '',
            total_sum: '',
            delivery_sum: '',
            items: '',
            venue_id: '',
            time_picker_value: '',
            comment: ''
        }
    },

    setValidationInfo(validationSum, deliverySum, deliverySumStr, promos) {
        this.validationSum = validationSum;
        this.deliverySum = deliverySum;
        this.deliverySumStr = deliverySumStr;
        this.promos = promos;
    }

}, action => {
    switch (action.actionType) {
        case Actions.UPDATE:
            if (action.data.request == "order") {
                OrderStore.setValidationInfo(
                    action.data.total_sum,
                    action.data.delivery_sum,
                    action.data.delivery_sum_str,
                    action.data.promos
                );
            }
            break;
    }
});

export default OrderStore;
