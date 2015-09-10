import Map from 'es6-map';
import Actions from '../Actions';
import BaseStore from './BaseStore';

const ORDER_STATUS = {
        NEW: 0,
        READY: 1,
        CANCELED_BY_CLIENT: 2,
        CANCELED_BY_RESTAURANT: 3,
        CONFIRMED: 5
    },
    ORDER_STATUS_NAMES = {
        [ORDER_STATUS.NEW]: "Новый",
        [ORDER_STATUS.READY]: "Выдан",
        [ORDER_STATUS.CANCELED_BY_CLIENT]: "Отменен клиентом",
        [ORDER_STATUS.CANCELED_BY_RESTAURANT]: "Отменен рестораном",
        [ORDER_STATUS.CONFIRMED]: "Подтвержден"
    },
    ORDER_DELIVERY_TYPE = {
        TAKEOUT: 0,
        IN_CAFE: 1,
        DELIVERY: 2
    },
    ORDER_DELIVERY_TYPE_NAMES = {
        [ORDER_DELIVERY_TYPE.TAKEOUT]: "С собой",
        [ORDER_DELIVERY_TYPE.IN_CAFE]: "В кафе",
        [ORDER_DELIVERY_TYPE.DELIVERY]: "Доставка"
    },
    ORDER_PAYMENT_TYPE = {
        CASH: 0,
        CARD: 1,
        PAYPAL: 4
    },
    ORDER_PAYMENT_TYPE_NAMES = {
        [ORDER_PAYMENT_TYPE.CASH]: "Наличными",
        [ORDER_PAYMENT_TYPE.CARD]: "Картой",
        [ORDER_PAYMENT_TYPE.PAYPAL]: "PayPal"
    };

class Order {
    constructor(obj) {
        this.id = obj.order_id;
        this.number = obj.number;
        this.status = obj.status;
        this.deliveryType = obj.delivery_type;
        this.address = obj.address;
        this.deliveryTime = obj.delivery_time;
        this.paymentType = obj.payment_type_id;
        this.total = obj.total;
        this.walletPayment = obj.wallet_payment;
        this.deliverySum = obj.delivery_sum;
        this.items = obj.items;
        this.gifts = obj.gifts;
        this.client = obj.client;
        this.comment = obj.comment;
        this.returnComment = obj.return_comment;
    }

    get statusName() {
        return OrderStore.STATUS_NAMES[this.status];
    }

    get deliveryTypeName() {
        return OrderStore.DELIVERY_TYPE_NAMES[this.deliveryType];
    }

    get paymentTypeName() {
        return OrderStore.PAYMENT_TYPE_NAMES[this.paymentType];
    }

    get paymentSum() {
        return this.total - this.walletPayment;
    }
}

const OrderStore = new BaseStore({
    STATUS: ORDER_STATUS,
    STATUS_NAMES: ORDER_STATUS_NAMES,
    DELIVERY_TYPE: ORDER_DELIVERY_TYPE,
    DELIVERY_TYPE_NAMES: ORDER_DELIVERY_TYPE_NAMES,
    PAYMENT_TYPE: ORDER_PAYMENT_TYPE,
    PAYMENT_TYPE_NAMES: ORDER_PAYMENT_TYPE_NAMES,

    _knownOrders: new Map(),
    lastServerTimestamp: null,
    _addOrders(array) {
        for (let rawOrder of array) {
            let o = new Order(rawOrder);
            this._knownOrders.set(o.id, o);
        }
    },
    _setTimestamp(newTimestamp) {
        this.lastServerTimestamp = newTimestamp;
    },

    loadCurrent(orders, timestamp) {
        this._addOrders(orders);
        this._setTimestamp(timestamp);
        this._changed();
    },
    loadUpdates(newOrders, updates, timestamp) {
        this._addOrders(newOrders);
        this._addOrders(updates);
        this._setTimestamp(timestamp);
        this._changed();
    },

    _getOrders(filter) {
        const result = [];
        for (let o of this._knownOrders.values()) {
            if (filter(o)) {
                result.push(o);
            }
        }
        result.sort((a, b) => a.deliveryTime - b.deliveryTime);
        return result;
    },
    getOrderAheadOrders() {
        return this._getOrders(o => o.deliveryType != this.DELIVERY_TYPE.DELIVERY);
    },
    getDeliveryOrders() {
        return this._getOrders(o => o.deliveryType == this.DELIVERY_TYPE.DELIVERY);
    }
}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == 'current') {
                OrderStore.loadCurrent(action.data.orders, action.data.timestamp);
            }
            if (action.data.request == 'updates') {
                OrderStore.loadUpdates(action.data.new_orders, action.data.updated, action.data.timestamp);
            }
            break;
    }
});
export default OrderStore;
