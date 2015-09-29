import BaseStore from './BaseStore';
import Actions from '../Actions';
import ClientStore from './ClientStore';
import VenuesStore from './VenuesStore';
import PaymentsStore from './PaymentsStore';
import MenuItemStore from './MenuItemStore';
import AddressStore from './AddressStore';
import assign from 'object-assign';

const OrderStore = new BaseStore({
    orderId: null,
    validationSum: 0,
    deliverySum: 0,
    deliverySumStr: '',
    items: [],
    orderGifts: [],
    slotId: null,
    dayStr: null,
    timeStr: null,
    promos: [],
    errors: [],
    orderError: null,

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

    getValidationTotalSum() {
        return this.validationSum;
    },

    getDeliverySum() {
        return this.deliverySum;
    },

    getDeliverySumStr() {
        return this.deliverySumStr;
    },

    getItems() {
        return this.items;
    },

    getOrderGifts() {
        return this.orderGifts;
    },

    getOrderGiftsDict() {
        return this.getOrderGifts().map(item => {
            return {
                quantity: item.quantity,
                item_id: item.id,
                group_modifiers: item.group_modifiers.map(modifier => {
                    return {
                        quantity: 1,
                        group_modifier_id: modifier.id,
                        choice: modifier.choice
                    };
                }),
                single_modifiers: []
            }
        });
    },

    getPromos() {
        return this.promos;
    },

    getErrors() {
        return this.errors;
    },

    getOrderError() {
        return this.orderError;
    },

    getGroupModifierDict(item) {
        return item.group_modifiers.map(modifier => {
            var choice_id;
            if (modifier.chosen_choice != null) {
                choice_id = modifier.chosen_choice.id
            } else {
                choice_id = MenuItemStore.getDefaultModifierChoice(modifier).id;
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
        Actions.checkOrder();
        this._changed();
    },

    addItem(item, totalSum) {
        item.totalSum = totalSum;
        this.items.push(item);
        this.validationSum = this.totalSum;
        Actions.checkOrder();
        this._changed();
    },

    removeItem(item) {
        this.items.splice(this.items.indexOf(item), 1);
        this.validationSum = this.totalSum;
        Actions.checkOrder();
        this._changed();
    },

    getOrderDict() {
        var delivery = VenuesStore.getChosenDelivery();
        var dict = {
            delivery_type: delivery.id,
            client: ClientStore.getClientDict(),
            payment: PaymentsStore.getPaymentDict(),
            device_type: 2,
            total_sum: this.getValidationTotalSum(),
            items: this.getItemsDict(),
            order_gifts: this.getOrderGiftsDict(),
            comment: ''
        };
        if (delivery.id == 2) {
            assign(dict, {
                delivery_sum: this.getDeliverySum(),
                address: AddressStore.getAddressDict()
            });
        } else {
            assign(dict, {
                venue_id: VenuesStore.getChosenVenue().id
            });
        }
        if (delivery.slots.length > 0) {
            assign(dict, {
                delivery_slot_id: this.getSlotId()
            });
        } else {
            assign(dict, {
                time_picker_value: this.getFullTimeStr()
            });
        }
        return dict;
    },

    getCheckOrderDict() {
        var delivery = VenuesStore.getChosenDelivery();
        var dict = {
            client_id: ClientStore.getClientId(),
            delivery_type: VenuesStore.getChosenDelivery().id,
            payment: JSON.stringify(PaymentsStore.getPaymentDict()),
            items: JSON.stringify(this.getItemsDict())
        };
        if (delivery.id == 2) {
            assign(dict, {
                address: JSON.stringify(AddressStore.getAddressDict())
            });
        } else {
            assign(dict, {
                venue_id: VenuesStore.getChosenVenue().id
            });
        }
        if (delivery.slots.length > 0) {
            assign(dict, {
                delivery_slot_id: this.getSlotId()
            });
        } else {
            assign(dict, {
                time_picker_value: this.getFullTimeStr()
            });
        }
        return dict;
    },

    setValidationInfo(validationSum, orderGifts, deliverySum, deliverySumStr, promos, errors) {
        this.validationSum = validationSum;
        this.orderGifts = orderGifts;
        this.deliverySum = deliverySum;
        this.deliverySumStr = deliverySumStr;
        this.promos = promos;
        this.errors = errors;
        this.orderError = null;
        this._changed();
    },

    setOrderError(error) {
        this.orderError = error;
        this._changed();
    },

    setOrderId(orderId) {
        this.orderId = orderId;
        this.orderError = null;
        this._changed();
        Actions.setOrderSuccess(orderId);
    },

    getOrderId() {
        return this.orderId;
    },

    setDay(date) {
        this.dayStr = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
        Actions.checkOrder();
        this._changed();
    },

    setTime(date) {
        this.timeStr = `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
        Actions.checkOrder();
        this._changed();
    },

    getFullTimeStr() {
        if (this.dayStr == null) {
            this.setDay(new Date());
        }
        if (this.timeStr == null) {
            var now = new Date();
            var delivery = VenuesStore.getChosenDelivery();
            now.setTime(now.getTime() + (delivery.time_picker_min * 1000));
            this.setTime(now);
        }
        return `${this.dayStr} ${this.timeStr}`;
    }

}, action => {
    switch (action.actionType) {
        case Actions.UPDATE:
            if (action.data.request == "order") {
                OrderStore.setValidationInfo(
                    action.data.total_sum,
                    action.data.orderGifts,
                    action.data.delivery_sum,
                    action.data.delivery_sum_str,
                    action.data.promos,
                    action.data.errors
                );
            }
            break;
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "order") {
                OrderStore.setOrderId(action.data.orderId);
            }
            break;
        case Actions.ERROR:
            if (action.data.request == "order") {
                OrderStore.setOrderError(action.data.error);
            }
            break;
    }
});

export default OrderStore;
