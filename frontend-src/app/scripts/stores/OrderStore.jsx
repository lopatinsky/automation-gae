import BaseStore from './BaseStore';
import Actions from '../Actions';
import ClientStore from './ClientStore';
import VenuesStore from './VenuesStore';
import PaymentsStore from './PaymentsStore';

const OrderStore = new BaseStore({
    orderId: null,
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
        var totalSum = 0;
        for (var i = 0; i < this.items.length; i++) {
            totalSum += this.items[i].totalSum;
        }
        return totalSum;
    },

    getDeliverySum() {
        return this.deliverySum;
    },

    getItems() {
        return this.items;
    },

    getGroupModifierDict(item) {
        return item.group_modifiers.map(modifier => {
            var choice_id;
            if (modifier.chosen_choice != null) {
                choice_id = modifier.chosen_choice.id
            } else {
                choice_id = MenuItemStore.getDefaultModifierChoice();
            }
            return {
                quantity: 1,
                group_modifier_id: modifier.modifier_id,
                choice: choice_id
            };
        });
    },

    getSingleModifierDict(item) {
        var modifiers = [];
        for (var i = 0; i < item.single_modifiers.length; i++) {
            if (item.single_modifiers[i].quantity > 0) {
                modifiers.push({
                    single_modifier_id: item.single_modifiers[i].modifier_id,
                    quantity: item.single_modifiers[i].quantity
                })
            }
        }
        return modifiers;
    },

    getItemsDict() {
        return this.getItems().map(item => {
            return {
                quantity: 1,
                item_id: item.id,
                single_modifiers: this.getSingleModifierDict(item),
                group_modifiers: this.getGroupModifierDict(item)
            }
        });
    },

    setSlotId(slotId) {
        this.slotId = slotId;
        this._changed();
    },

    addItem(item, totalSum) {
        item.totalSum = totalSum;
        this.items.push(item);
        this.validationSum = this.totalSum;
        this._changed();
    },

    removeItem(item) {
        this.items.splice(this.items.indexOf(item), 1);
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
