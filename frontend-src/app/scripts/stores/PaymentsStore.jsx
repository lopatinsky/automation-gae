import BaseStore from './BaseStore';
import Actions from '../Actions';
import assign from 'object-assign';

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

    getChosenPaymentTypeTitle() {
        return this.chosen_payment_type.really_title;
    },

    getChosenPaymentType() {
        return this.chosen_payment_type;
    },

    setChosenPaymentType(payment_type) {
        this.chosen_payment_type = payment_type;
        Actions.checkOrder();
        this._changed();
    },

    getPaymentDict() {
        var paymentType = this.getChosenPaymentType();
        var dict = {};
        if (paymentType != null) {
            assign(dict, {
                type_id: paymentType.id
            });
        }
        return dict;
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