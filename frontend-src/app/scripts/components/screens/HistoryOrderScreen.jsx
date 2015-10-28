import React from 'react';
import { Card, CardText, RefreshIndicator, Dialog, FlatButton, RaisedButton, Snackbar, FontIcon, ListDivider } from 'material-ui';
import { OrderStore, HistoryStore, VenuesStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { SuccessPlaceOrderDialog, LoadingDialog } from '../dialogs';
import HistoryOrderItem from './HistoryOrderItem';
import settings from '../../settings';

const HistoryOrderScreen = React.createClass({
    refresh() {
        var order = this.props.order;
        if (OrderStore.getOrderId() != null) {
            if (order != null && OrderStore.getOrderId() == order.order_id) {
                this.refs.doneProcessingDialog.dismiss();
                this.refs.successDialog.show();
                 OrderStore.clearOrderId();
            } else {
                this.refs.doneProcessingDialog.show();
            }

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
        ServerRequests.cancelOrder(order.order_id);
    },

    _getVenueOutput(order) {
        var address = '';
        if (order.address == null && order.venue_id != '' && order.venue_id != null) {
            var venue = VenuesStore.getVenue(order.venue_id);
            if (venue != null) {
               address = venue.address;
            }
        } else {
            if (order.address != null) {
                address = order.address.formatted_address;
            }
        }
        return <div style={{display: 'table', padding: '12px'}}>
            <FontIcon style={{display: 'table-cell', fontSize: '18px', verticalAlign: 'middle'}}
                      color={settings.primaryColor}
                      className="material-icons">
                location_on
            </FontIcon>
            <div style={{display: 'table-cell', padding: '0 0 0 6px'}}>
                {address}
            </div>
        </div>;
    },

    getOrder() {
        var order = this.props.order;
        if (order != null) {
            return <Card>
                <div style={{padding: '12px'}}>
                    Заказ <b style={{color: settings.primaryColor}}>#{order.number}</b>
                    <div style={{float: 'right'}}>
                        <b>{HistoryStore.getStatus(order.status)}</b>
                    </div>
                </div>
                <ListDivider/>
                <div>
                    {order.items.map(item => {
                        return <HistoryOrderItem item={item} />;
                    })}
                </div>
                <ListDivider/>
                <div style={{padding: '12px', height: '48px'}}>
                    <div style={{float: 'right'}}>
                        {'Итого: ' + order.total}
                    </div>
                </div>
                <ListDivider/>
                <div style={{padding: '12px'}}>
                    {'Готов к ' + order.delivery_time_str}
                </div>
                <ListDivider/>
                {this._getVenueOutput(order)}
            </Card>;
        } else {
             return <RefreshIndicator size={40} left={80} top={5} status="loading" />
        }
    },

    getCancelButton() {
        var order = this.props.order;
        if (order && order.status == 0) {
            return <div style={{float: 'right', padding: '12px'}}>
                <RaisedButton label='Отмена'
                              primary={true}
                              onClick={this.cancel} />
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
            <SuccessPlaceOrderDialog ref="successDialog" />
            <LoadingDialog
                ref="doneProcessingDialog"
                title="Загрузка заказа"/>
            <LoadingDialog
                ref="cancelProcessingDialog"
                title="Отмена заказа"/>
            <Snackbar
                ref='cancelSnackBar'
                style={{padding: '6px', width: '100%', marginLeft: '0', bottom: '0', textAlign: 'center', maxHeight: '128px', height: null, lineHeight: '175%'}}
                message={OrderStore.getCancelDescription()}
                onDismiss={() => {OrderStore.setCancelDescription(null)}}/>
        </div>;
    }
});

export default HistoryOrderScreen;