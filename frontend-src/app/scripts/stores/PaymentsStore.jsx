import BaseStore from './BaseStore';
import OrderStore from './OrderStore';
import { ServerRequests } from '../actions';

const PaymentsStore = new BaseStore({
    SUPPORTED_PAYMENT_TYPES: {
        0: 'Наличными',
        5: 'Картой курьеру'
    },

    payment_types: [],

    getTitle(paymentTypeId) {
        return this.SUPPORTED_PAYMENT_TYPES[paymentTypeId]
    },

    _setPaymentTypes(payment_types) {
        const filteredPaymentTypes = [];
        for (let paymentType of payment_types) {
            if (paymentType.id in this.SUPPORTED_PAYMENT_TYPES) {
                filteredPaymentTypes.push(paymentType);
            }
        }
        this.payment_types = filteredPaymentTypes;
        this._changed();
    }
}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "payment_types") {
                PaymentsStore._setPaymentTypes(action.data.payment_types);
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            break;
    }
});

export default PaymentsStore;