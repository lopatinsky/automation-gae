import React from 'react';
import { Card, CardText, RefreshIndicator, Dialog, FlatButton, Snackbar } from 'material-ui';
import { OrderStore } from '../stores';
import Actions from '../Actions';

const HistoryOrderScreen = React.createClass({
    refresh() {
        var order = this.props.order;
        if (order != null && OrderStore.getOrderId() == order.order_id) {
            this.refs.successDialog.show();
            OrderStore.clearOrderId();
        }
        if (OrderStore.getCancelProcessing()) {
            this.refs.cancelProcessingDialog.show();
        } else {
            this.refs.cancelProcessingDialog.dismiss();
        }
        if (OrderStore.getCancelDescription()) {
            this.refs.cancelSnackBar.show();
        }
        this.setState({});
    },

    cancel() {
        OrderStore.setCancelProcessing();
        var order = this.props.order;
        Actions.cancelOrder(order.order_id);
    },

    getOrder() {
        var order = this.props.order;
        if (order != null) {
            return <Card>
                <CardText>
                    Заказ {order.number}
                </CardText>
            </Card>;
        } else {
             return <RefreshIndicator size={40} left={80} top={5} status="loading" />
        }
    },

    getCancelButton() {
        var order = this.props.order;
        if (order && order.status == 0) {
            return <div>
                <FlatButton label='Отмена' onClick={this.cancel} />
            </div>;
        } else {
            return <div/>;
        }
    },

    componentDidMount() {
        OrderStore.addChangeListener(this.refresh);
        this.refresh();
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this.refresh);
    },


    render() {
        return <div style={{padding: '64px 0 0 0'}}>
            {this.getOrder()}
            {this.getCancelButton()}
            <Dialog
                ref="successDialog"
                title="Заказ успешно размещен"/>
            <Dialog
                ref="cancelProcessingDialog"
                title="Отмена заказа">
                <RefreshIndicator left={5} top={5} status="loading" />
            </Dialog>
            <Snackbar
                ref='cancelSnackBar'
                message={OrderStore.getCancelDescription()}
                autoHideDuration='1000'
                onDismiss={() => {OrderStore.setCancelDescription(null)}}/>
        </div>;
    }
});

export default HistoryOrderScreen;