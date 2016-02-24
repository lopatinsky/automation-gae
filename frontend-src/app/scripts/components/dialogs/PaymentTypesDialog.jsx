import React from 'react';
import { Dialog, List, ListItem, ListDivider } from 'material-ui';
import { PaymentsStore } from '../../stores';

const PaymentTypesDialog = React.createClass({
    getInitialState() {
        return {
            open: false
        };
    },

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
        this.setState({
            open: true
        });
    },

    dismiss(payment_type) {
        PaymentsStore.setChosenPaymentType(payment_type);
        this.setState({
            open: false
        });
    },

    render() {
        return (
            <Dialog
                bodyStyle={{padding: '12px'}}
                open={this.state.open}
                ref="paymentTypesDialog">
                <List>
                    {this._getPaymentTypes()}
                </List>
            </Dialog>
        );
    }
});

export default PaymentTypesDialog;