import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';
import ClientStore from './ClientStore';
import VenuesStore from './VenuesStore';
import PaymentsStore from './PaymentsStore';
import MenuItemStore from './MenuItemStore';
import AddressStore from './AddressStore';

const OrderStore = new BaseStore({
    orderId: null,
    validationSum: 0,
    deliverySum: 0,
    deliverySumStr: '',
    items: [],
    comment: '',
    orderGifts: [],
    slotId: null,
    dayStr: null,
    timeStr: null,
    promos: [],
    errors: [],
    orderError: null,
    cancelProcessing: false,
    cancelDescription: null,

    getSlotId() {
        return this.slotId;
    },

    getTotalSum() {
        var totalSum = 0;
        for (var i = 0; i < this.items.length; i++) {
            totalSum += this.items[i].price * this.items[i].quantity;
            for (var j = 0; j < this.items[i].single_modifiers.length; j++) {
                if (this.items[i].single_modifiers[j].quantity > 0) {
                    totalSum += this.items[i].single_modifiers[j].price * this.items[i].single_modifiers[j].quantity * this.items[i].quantity;
                }
            }
            for (j = 0; j < this.items[i].group_modifiers.length; j++) {
                totalSum += this.items[i].group_modifiers[j].chosen_choice.price *  this.items[i].quantity;
            }
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

    getCancelDescription() {
        return this.cancelDescription;
    },

    getCancelProcessing() {
        return this.cancelProcessing;
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
                quantity: item.quantity,
                item_id: item.id,
                single_modifiers: this.getSingleModifierDict(item),
                group_modifiers: this.getGroupModifierDict(item)
            }
        });
    },

    setSlotId(slotId) {
        this.slotId = slotId;
        ServerRequests.checkOrder();
        this._changed();
    },

    addItem(item) {
        for (i = 0; i < item.group_modifiers.length; i++) {
            if (item.group_modifiers[i].chosen_choice == null) {
                item.group_modifiers[i].chosen_choice = MenuItemStore.getDefaultModifierChoice(item.group_modifiers[i]);
            }
        }
        var found = false;
        for (var i = 0; i < this.items.length; i++) {
            if (this.compareItems(item, this.items[i]) == true) {
                this.items[i].quantity += 1;
                found = true;
            }
        }
        if (found == false) {
            item.quantity = 1;
            this.items.push(JSON.parse(JSON.stringify(item)));
        }
        this.validationSum = this.getTotalSum();
        ServerRequests.checkOrder();
        this._changed();
    },

    removeItem(item) {
        this.items.splice(this.items.indexOf(item), 1);
        this.validationSum = this.getTotalSum();
        ServerRequests.checkOrder();
        this._changed();
    },

    compareItems(item1, item2) {
        if (item1.id != item2.id) {
            return false;
        }
        var modifiers1 = item1.group_modifiers;
        var modifiers2 = item2.group_modifiers;
        if (modifiers1.length != modifiers2.length) {
            return false;
        }
        for (var i = 0; i < modifiers1.length; i++) {
            if (modifiers1[i].chosen_choice.id != modifiers2[i].chosen_choice.id) {
                return false;
            }
        }
        modifiers1 = item1.single_modifiers;
        modifiers2 = item2.single_modifiers;
        if (modifiers1.length != modifiers2.length) {
            return false;
        }
        for (i = 0; i < modifiers1.length; i++) {
            if (modifiers1[i].quantity != modifiers2[i].quantity) {
                return false;
            }
        }
        return true;
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
            dict.delivery_sum = this.getDeliverySum();
            dict.address = AddressStore.getAddressDict();
        } else {
            dict.venue_id = VenuesStore.getChosenVenue().id;
        }
        if (delivery.slots.length > 0) {
            dict.delivery_slot_id = this.getSlotId();
        } else {
            dict.time_picker_value = this.getFullTimeStr();
        }
        return dict;
    },

    getCheckOrderDict() {
        var delivery = VenuesStore.getChosenDelivery();
        var client_id = ClientStore.getClientId();
        if (!delivery || !client_id) {
            return null;
        }
        var dict = {
            client_id: client_id,
            delivery_type: delivery.id,
            payment: JSON.stringify(PaymentsStore.getPaymentDict()),
            items: JSON.stringify(this.getItemsDict())
        };
        if (delivery.id == 2) {
            dict.address = JSON.stringify(AddressStore.getAddressDict());
        } else {
            dict.venue_id = VenuesStore.getChosenVenue().id;
        }
        if (delivery.slots.length > 0) {
            dict.delivery_slot_id = this.getSlotId();
        } else {
            dict.time_picker_value = this.getFullTimeStr();
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

    setCancelDescription(description) {
        this.cancelDescription = description;
        this._changed();
    },

    setCancelProcessing() {
        this.cancelProcessing = true;
        this._changed();
    },

    clearCancelProcessing() {
        this.cancelProcessing = false;
        this._changed();
    },

    setOrderId(orderId) {
        this.orderId = orderId;
        this.orderError = null;
        this._changed();
        ServerRequests.setOrderSuccess(orderId);
    },

    clearOrderId() {
        this.orderId = null;
    },

    setComment(comment) {
        this.comment = comment;
        this._changed();
    },

    getComment() {
        return this.comment;
    },

    getRenderedComment() {
        if (this.comment == null || this.comment == '') {
            return 'Комментарий';
        } else {
            return this.comment;
        }
    },

    getOrderId() {
        return this.orderId;
    },

    setDay(date) {
        this.dayStr = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
    },

    setTime(date) {
        this.timeStr = `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
        ServerRequests.checkOrder();
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
        case ServerRequests.UPDATE:
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
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "order") {
                OrderStore.setOrderId(action.data.orderId);
            }
            break;
        case ServerRequests.ERROR:
            if (action.data.request == "order") {
                OrderStore.setOrderError(action.data.error);
            }
            break;
        case ServerRequests.CANCEL:
            if (action.data.request == "order") {
                OrderStore.setCancelDescription(action.data.description);
                OrderStore.clearCancelProcessing();
            }
            break;

    }
});

export default OrderStore;
