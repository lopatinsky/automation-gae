import BaseStore from './BaseStore';
import Actions from '../Actions';
import ClientStore from './ClientStore';
import VenuesStore from './VenuesStore';
import PaymentsStore from './PaymentsStore';

const OrderStore = new BaseStore({
    orderId: null,
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

    getDeliverySum() {
        return this.deliverySum;
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
            delivery_type: VenuesStore.getChosenDelivery().id,
            client: ClientStore.getClientDict(),
            payment: PaymentsStore.getPaymentDict(),
            device_type: 2,
            delivery_slot_id: this.getSlotId(),
            total_sum: this.getTotalSum(),
            delivery_sum: this.getDeliverySum(),
            items: this.getItemsDict(),
            venue_id: VenuesStore.getChosenVenue().id,
            //time_picker_value: '',
            comment: ''
        }
    },

    setValidationInfo(validationSum, deliverySum, deliverySumStr, promos) {
        this.validationSum = validationSum;
        this.deliverySum = deliverySum;
        this.deliverySumStr = deliverySumStr;
        this.promos = promos;
        Actions.order();
    },

    setOrderId(orderId) {
        this.orderId = orderId;
        this._changed();
    },

    getOrderId() {
        return this.orderId;
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
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "order") {
                OrderStore.setOrderId(action.data.orderId);
            }
            break;
    }
});

export default OrderStore;
