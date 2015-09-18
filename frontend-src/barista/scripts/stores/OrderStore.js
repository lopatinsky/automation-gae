import moment from 'moment';
import _ from 'moment/locale/ru';
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
        this.deliveryTime = moment(obj.delivery_time * 1000);
        this.paymentType = obj.payment_type_id;
        this.total = obj.total;
        this.walletPayment = obj.wallet_payment;
        this.deliverySum = obj.delivery_sum;
        this.items = obj.items;
        this.gifts = obj.gifts;
        this.client = obj.client;
        this.client.phone = Order._formatPhone(this.client.phone);
        this.comment = obj.comment;
        this.returnComment = obj.return_comment;
        this.address = obj.address ? obj.address.formatted_address : null;
    }

    static _formatPhone(str) {
        if (str.length != 11) {
            return str;
        }
        const parts = ['8', str.substring(1, 4), str.substring(4, 7), str.substring(7, 9), str.substring(9, 11)];
        return `${parts[0]} ${parts[1]} ${parts[2]}-${parts[3]}-${parts[4]}`;
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
    _addOrder(order) {
        if (order.status == this.STATUS.NEW || order.status == this.STATUS.CONFIRMED) {
            this._knownOrders.set(order.id, order);
        } else {
            this._knownOrders.delete(order.id);
        }
    },
    _addRawOrders(array) {
        for (let rawOrder of array) {
            this._addOrder(new Order(rawOrder));
        }
    },
    _setTimestamp(newTimestamp) {
        this.lastServerTimestamp = newTimestamp;
    },

    loadCurrent(orders, timestamp) {
        this._addRawOrders(orders);
        this._setTimestamp(timestamp);
        this._changed();
    },
    loadUpdates(newOrders, updates, timestamp) {
        this._addRawOrders(newOrders);
        this._addRawOrders(updates);
        this._setTimestamp(timestamp);
        this._changed();
    },

    _saveAndChanged(order) {
        this._addOrder(order);
        this._changed();
    },
    close(order) {
        order.status = this.STATUS.DONE;
        this._saveAndChanged(order);
    },
    postpone(order, { mins }) {
        order.deliveryTime.add(mins, 'minutes');
        this._saveAndChanged(order);
    },
    cancel(order) {
        order.status = this.STATUS.CANCELED_BY_RESTAURANT;
        this._saveAndChanged(order);
    },
    confirm(order) {
        order.status = this.STATUS.CONFIRMED;
        this._saveAndChanged(order);
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
            if (action.data.request.substring(0, 13) == 'order_action_') {
                OrderStore[action.data.action](action.data.order, action.data.options);
            }
            break;
    }
});
export default OrderStore;
