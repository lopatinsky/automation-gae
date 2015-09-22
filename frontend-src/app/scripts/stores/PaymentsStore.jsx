import BaseStore from './BaseStore';
import Actions from '../Actions';

const PaymentsStore = new BaseStore({
    payment_types: [],
    chosen_payment_type: null,

    _setPaymentTypes(payment_types) {
        this.payment_types = payment_types;
        if (payment_types.length > 0) {
            this.chosen_payment_type = payment_types[0];
        }
    },

    getPaymentTypes() {
        return this.payment_types;
    },

    getChosenPaymentType() {
        return this.chosen_payment_type;
    },

    setChosenPaymentType(payment_type) {
        this.chosen_payment_type = payment_type;
        this._changed();
    },

    getPaymentDict() {
        return {
            type_id: this.getChosenPaymentType().id
        }
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "payment_types") {
                PaymentsStore._setPaymentTypes(action.data.payment_types);
            }
            break;
        case Actions.AJAX_FAILURE:
            alert('failure');
            break;
    }
});

export default PaymentsStore;