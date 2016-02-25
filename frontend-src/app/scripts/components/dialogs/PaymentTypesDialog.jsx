import React from 'react';
import { Dialog, List, ListItem, Divider } from 'material-ui';
import { PaymentsStore } from '../../stores';

const PaymentTypesDialog = React.createClass({
    getInitialState() {
        return {
            open: false
        };
    },

    _getPaymentTypes() {
        var payment_types = PaymentsStore.getPaymentTypes();
        const result = [];
        for (let pt of payment_types) {
            result.push(<ListItem key={pt.id}
                                  primaryText={pt.really_title}
                                  onClick={() => this.dismiss(pt)}/>);
            result.push(<Divider key={`divider_${pt.id}`}/>)
        }
        result.pop();
        return result;
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