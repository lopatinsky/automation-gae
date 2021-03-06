import AppDispatcher from '../AppDispatcher';
import BaseStore from './BaseStore';
import { AppActions, ServerRequests } from '../actions';
import ClientStore from './ClientStore';
import VenuesStore from './VenuesStore';
import PaymentsStore from './PaymentsStore';
import MenuStore from './MenuStore';
import AddressStore from './AddressStore';
import CompanyStore from './CompanyStore';

const OrderStore = new BaseStore({
    sendingCheckOrder: null,
    sendingOrder: null,

    chosenPaymentType: null,
    chosenVenue: null,
    chosenDeliveryType: null,
    validationSum: 0,
    deliverySum: 0,
    deliverySumStr: '',
    items: [],
    comment: '',
    orderGifts: [],
    chosenTime: null,
    promos: [],
    errors: [],

    onPaymentTypesLoaded() {
        if (!this.chosenPaymentType && PaymentsStore.payment_types) {
            this.setChosenPaymentType(PaymentsStore.payment_types[0]);
        }
    },

    setChosenPaymentType(paymentType) {
        this.chosenPaymentType = paymentType;
        this._changed({checkOrder: true});
    },

    onVenuesLoaded() {
        if (!this.chosenVenue && VenuesStore.venues.length) {
            this.setChosenVenue(VenuesStore.venues[0]);
        }
    },

    onCompanyLoaded() {
        const deliveryTypes = CompanyStore.getDeliveryTypes();
        if (!this.chosenDeliveryType && deliveryTypes.length) {
            this.setChosenDeliveryType(deliveryTypes[0]);
        }
    },

    setChosenDeliveryType(deliveryType) {
        if (!this.chosenDeliveryType || this.chosenDeliveryType.id != deliveryType.id) {
            this.chosenDeliveryType = deliveryType;
            this.setTime(null);
        }
    },

    setChosenVenue(venue) {
        this.chosenVenue = venue;
        this._changed({checkOrder: true});
    },

    getPaymentDict() {
        var paymentType = this.chosenPaymentType;
        var dict = {};
        if (paymentType != null) {
            dict.type_id = paymentType.id;
        }
        return dict;
    },

    getTotalSum() {
        var totalSum = 0;
        for (let orderItem of this.items) {
            totalSum += orderItem.quantity * MenuStore.getItemPrice(
                orderItem.item,
                orderItem.groupModifiers,
                orderItem.singleModifiers);
        }
        return totalSum;
    },

    getOrderGiftsDict() {
        return this.orderGifts.map(item => {
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

    getGroupModifierDict(orderItem) {
        var modifiers = [];
        for (const gm of orderItem.item.group_modifiers) {
            const choice = orderItem.groupModifiers[gm.modifier_id];
            if (choice) {
                modifiers.push({
                    quantity: 1,
                    group_modifier_id: gm.modifier_id,
                    choice: choice.id
                });
            }
        }
        return modifiers;
    },

    getSingleModifierDict(orderItem) {
        var modifiers = [];
        for (const sm of orderItem.item.single_modifiers) {
            const quantity = orderItem.singleModifiers[sm.modifier_id];
            if (quantity) {
                modifiers.push({
                    single_modifier_id: sm.modifier_id,
                    quantity: quantity
                })
            }
        }
        return modifiers;
    },

    getItemsDict() {
        return this.items.map(orderItem => {
            return {
                quantity: orderItem.quantity,
                item_id: orderItem.item.id,
                single_modifiers: this.getSingleModifierDict(orderItem),
                group_modifiers: this.getGroupModifierDict(orderItem)
            }
        });
    },

    setSlotId(slotId) {
        this.slotId = slotId;
        this._changed({checkOrder: true});
    },

    addItem(itemId, groupModifiers, singleModifiers) {
        const item = MenuStore.itemsById[itemId];
        if (!groupModifiers) {
            [groupModifiers, singleModifiers] = MenuStore.getDefaultModifiers(item);
        }
        const orderItem = {
                item,
                groupModifiers,
                singleModifiers
            };

        var found = false;
        for (let existingItem of this.items) {
            if (this.compareItems(orderItem, existingItem)) {
                existingItem.quantity += 1;
                found = true;
            }
        }
        if (!found) {
            orderItem.quantity = 1;
            this.items.push(orderItem);
        }
        this.validationSum = this.getTotalSum();
        this._changed({checkOrder: true});
    },

    removeItem(item) {
        this.items.splice(this.items.indexOf(item), 1);
        this.validationSum = this.getTotalSum();
        this._changed({checkOrder: true});
    },

    compareItems(orderItem1, orderItem2) {
        if (orderItem1.item.id != orderItem2.item.id) {
            return false;
        }
        let item = orderItem1.item;
        for (let gm of item.group_modifiers) {
            if (orderItem1.groupModifiers[gm.modifier_id] != orderItem2.groupModifiers[gm.modifier_id]) {
                return false;
            }
        }
        for (let sm of item.single_modifiers) {
            if (orderItem1.singleModifiers[sm.modifier_id] != orderItem2.singleModifiers[sm.modifier_id]) {
                return false;
            }
        }
        return true;
    },

    getOrderDict() {
        var delivery = this.chosenDeliveryType;
        if (! ClientStore.getName()) {
            return [false, 'Введите Ваше имя'];
        } else if (! ClientStore.getPhone()) {
            return [false, 'Введите номер телефона'];
        }
        var dict = {
            delivery_type: delivery.id,
            client: ClientStore.getClientDict(),
            payment: this.getPaymentDict(),
            device_type: 2,
            total_sum: this.validationSum,
            items: this.getItemsDict(),
            order_gifts: this.getOrderGiftsDict(),
            comment: this.comment
        };
        if (delivery.id == 2) {
            dict.delivery_sum = this.deliverySum;
            dict.address = AddressStore.getAddressDict();
        } else {
            dict.venue_id = this.chosenVenue.id;
        }
        if (this.chosenTime) {
            if (delivery.mode == 0 || delivery.mode == 2 || delivery.mode == 3) {
                dict.delivery_slot_id = this.chosenTime.slotId;
            }
            if (delivery.mode == 1 || delivery.mode == 2) {
                dict.time_picker_value = this.chosenTime.picker.format("YYYY-MM-DD HH:mm:ss");
            }
        } else {
            return [false, 'Выберите время заказа'];
        }
        return [true, dict];
    },

    getCheckOrderDict() {
        var delivery = this.chosenDeliveryType;
        var client_id = ClientStore.getClientId();
        if (!delivery || !client_id) {
            return [false, 'Загружается...'];
        }
        var dict = {
            client_id: client_id,
            delivery_type: delivery.id,
            payment: JSON.stringify(this.getPaymentDict()),
            items: JSON.stringify(this.getItemsDict())
        };
        if (delivery.id == 2) {
            dict.address = JSON.stringify(AddressStore.getAddressDict());
        } else {
            if (!this.chosenVenue) {
                return [false, 'Загружается...'];
            }
            dict.venue_id = this.chosenVenue.id;
        }
        if (this.chosenTime) {
            if (delivery.mode == 0 || delivery.mode == 2 || delivery.mode == 3) {
                dict.delivery_slot_id = this.chosenTime.slotId;
            }
            if (delivery.mode == 1 || delivery.mode == 2) {
                dict.time_picker_value = this.chosenTime.picker.format("YYYY-MM-DD HH:mm:ss");
            }
        } else {
            return [false, 'Выберите время заказа'];
        }
        return [true, dict];
    },

    checkOrderStarted(requestObject) {
        if (this.sendingCheckOrder) {
            this.sendingCheckOrder.abort();
        }
        this.sendingCheckOrder = requestObject;
        this._changed();
    },

    _setValidationInfo(validationSum, orderGifts, deliverySum, deliverySumStr, promos, errors) {
        this.validationSum = validationSum;
        this.orderGifts = orderGifts.map(og => ({
            item: og,
            groupModifiers: {},
            singleModifiers: {},
            quantity: og.quantity
        }));
        this.deliverySum = deliverySum;
        this.deliverySumStr = deliverySumStr;
        this.promos = promos;
        this.errors = errors;
    },

    checkOrderFinished(validationSum, orderGifts, deliverySum, deliverySumStr, promos, errors) {
        this.sendingCheckOrder = null;
        if (validationSum != null) {
            this._setValidationInfo(validationSum, orderGifts, deliverySum, deliverySumStr, promos, errors);
        }
        this._changed();
    },

    orderStarted(requestObject) {
        if (this.sendingOrder) {
            this.sendingOrder.abort();
        }
        this.sendingOrder = requestObject;
        this._changed();
    },

    orderFinished(orderId) {
        this.sendingOrder = null;
        this.items = [];
        this._changed({orderId});
        setImmediate(() => ServerRequests.setOrderSuccess(orderId));
    },

    orderFailed(error) {
        this.sendingOrder = null;
        this._changed({orderError: error});
    },

    checkOrderNotReady(message) {
        if (this.sendingCheckOrder) {
            this.sendingCheckOrder.abort();
            this.sendingCheckOrder = null;
        }
        this._setValidationInfo(
            this.getTotalSum(),
            [],
            0, '',
            [], [message]
        );
        this._changed();
    },

    setComment(comment) {
        this.comment = comment;
        this._changed();
    },

    setTime(timeObj) {
        this.chosenTime = timeObj;
        this._changed({checkOrder: true});
    }
}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_DATA_NOT_READY:
            if (action.data.request == "checkOrder") {
                OrderStore.checkOrderNotReady(action.data.message);
            }
            if (action.data.request == "order") {
                OrderStore.orderFailed(action.data.message);
            }
            break;
        case ServerRequests.AJAX_SENDING:
            if (action.data.request == "checkOrder") {
                OrderStore.checkOrderStarted(action.data.requestObject);
            }
            if (action.data.request == "order") {
                OrderStore.orderStarted(action.data.requestObject);
            }
            break;
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "checkOrder") {
                OrderStore.checkOrderFinished(
                    action.data.total_sum,
                    action.data.orderGifts,
                    action.data.delivery_sum,
                    action.data.delivery_sum_str,
                    action.data.promos,
                    action.data.errors
                );
            }
            if (action.data.request == "order") {
                OrderStore.orderFinished(action.data.orderId);
            }
            if (action.data.request == "payment_types") {
                AppDispatcher.waitFor([PaymentsStore.dispatchToken]);
                OrderStore.onPaymentTypesLoaded();
            }
            if (action.data.request == "venues") {
                AppDispatcher.waitFor([VenuesStore.dispatchToken]);
                OrderStore.onVenuesLoaded();
            }
            if (action.data.request == "company") {
                AppDispatcher.waitFor([CompanyStore.dispatchToken]);
                OrderStore.onCompanyLoaded();
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            if (action.data.request == "checkOrder") {
                OrderStore.checkOrderFinished();
            }
            if (action.data.request == "order") {
                console.log(action.data);
                let error = null;
                if (action.data.err &&
                    action.data.err.response &&
                    action.data.err.response.body &&
                    action.data.err.response.body.description) {
                    error = action.data.err.response.body.description;
                } else {
                    error = 'Неизвестная ошибка при размещении заказа';
                }
                OrderStore.orderFailed(error);
            }
            break;
        case AppActions.SET_COMMENT:
            OrderStore.setComment(action.data.comment);
            break;
        case AppActions.SET_PAYMENT_TYPE:
            OrderStore.setChosenPaymentType(action.data.paymentType);
            break;
        case AppActions.SET_DELIVERY_TYPE:
            OrderStore.setChosenDeliveryType(action.data.deliveryType);
            break;
        case AppActions.SET_VENUE:
            OrderStore.setChosenVenue(action.data.venue);
            break;
        case AppActions.SET_TIME:
            OrderStore.setTime(action.data);
            break;
        case AppActions.ADD_ITEM:
            OrderStore.addItem(action.data.itemId, action.data.groupModifierChoices, action.data.singleModifierQuantities);
            break;
        case AppActions.REMOVE_ITEM:
            OrderStore.removeItem(action.data.item);
            break;
    }
});

export default OrderStore;
