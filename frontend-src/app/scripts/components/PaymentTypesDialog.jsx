import React from 'react';
import { Dialog} from 'material-ui';
import { List, ListItem } from 'material-ui';
import { PaymentsStore } from '../stores';

const PaymentTypesDialog = React.createClass({
    _getPaymentTypes() {
        var payment_types = PaymentsStore.getPaymentTypes();
        return payment_types.map(payment_type => {
            return (
                <ListItem
                    primaryText={payment_type.title}
                    onClick={() => this.dismiss(payment_type)}/>
            );
        });
    },

    show() {
        this.refs.paymentTypesDialog.show();
    },

    dismiss(payment_type) {
        PaymentsStore.setChosenPaymentType(payment_type);
        this.refs.paymentTypesDialog.dismiss();
    },

    render() {
        return (
            <Dialog ref="paymentTypesDialog">
                <List>
                    {this._getPaymentTypes()}
                </List>
            </Dialog>
        );
    }
});

export default PaymentTypesDialog;