import React from 'react';
import { Dialog, List, ListItem, ListDivider } from 'material-ui';
import { PaymentsStore } from '../../stores';

const PaymentTypesDialog = React.createClass({
    _getPaymentTypes() {
        var payment_types = PaymentsStore.getPaymentTypes();
        return payment_types.map(payment_type => {
            return (
                <div>
                    <ListItem
                        primaryText={payment_type.really_title}
                        onClick={() => this.dismiss(payment_type)}/>
                    <ListDivider/>
                </div>
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
            <Dialog
                bodyStyle={{padding: '12px'}}
                ref="paymentTypesDialog">
                <List>
                    {this._getPaymentTypes()}
                </List>
            </Dialog>
        );
    }
});

export default PaymentTypesDialog;