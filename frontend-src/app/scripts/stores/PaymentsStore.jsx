import BaseStore from './BaseStore';
import OrderStore from './OrderStore';
import { ServerRequests } from '../actions';

const PaymentsStore = new BaseStore({
    payment_types: [],

    _setPaymentTypes(payment_types) {
        this.payment_types = payment_types;
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