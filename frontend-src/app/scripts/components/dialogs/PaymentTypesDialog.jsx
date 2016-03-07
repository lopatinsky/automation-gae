import React from 'react';
import { Dialog, List, ListItem, Divider } from 'material-ui';
import { PaymentsStore } from '../../stores';
import { AppActions } from '../../actions';

const PaymentTypesDialog = React.createClass({
    getInitialState() {
        return {
            paymentTypes: PaymentsStore.payment_types,
            open: false
        };
    },

    _onPaymentsStoreChange() {
        this.setState({
            paymentTypes: PaymentsStore.payment_types
        });
    },

    componentDidMount() {
        PaymentsStore.addChangeListener(this._onPaymentsStoreChange);
    },

    componentWillUnmount() {
        PaymentsStore.removeChangeListener(this._onPaymentsStoreChange);
    },

    _getPaymentTypes() {
        const result = [];
        for (let pt of this.state.paymentTypes) {
            result.push(<ListItem key={pt.id}
                                  primaryText={PaymentsStore.getTitle(pt.id)}
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
                onRequestClose={() => this.setState({open: false})}
                ref="paymentTypesDialog">
                <List>
                    {this._getPaymentTypes()}
                </List>
            </Dialog>
        );
    }
});

export default PaymentTypesDialog;
