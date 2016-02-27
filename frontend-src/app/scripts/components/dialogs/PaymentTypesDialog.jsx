import React from 'react';
import { Dialog, List, ListItem, Divider } from 'material-ui';
import { PaymentsStore } from '../../stores';
import { AppActions } from '../../actions';

const PaymentTypesDialog = React.createClass({
    getInitialState() {
        return {
            open: false
        };
    },

    _getPaymentTypes() {
        var payment_types = PaymentsStore.payment_types;
        const result = [];
        for (let pt of payment_types) {
            result.push(<ListItem key={pt.id}
                                  primaryText={pt.really_title}
                                  onTouchTap={() => this.dismiss(pt)}/>);
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
        AppActions.setPaymentType(payment_type);
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