import React from 'react';
import CircularProgress from 'material-ui/lib/circular-progress';
import Divider from 'material-ui/lib/divider';
import FontIcon from 'material-ui/lib/font-icon';
import Paper from 'material-ui/lib/paper';
import { HistoryStore, VenuesStore, PaymentsStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { SuccessPlaceOrderDialog, LoadingDialog } from '../dialogs';
import HistoryOrderItem from './HistoryOrderItem';
import settings from '../../settings';

const HistoryOrderScreen = React.createClass({
    getInitialState() {
        return {
            order: HistoryStore.getOrder(this.props.orderId)
        };
    },

    _onHistoryStoreChange() {
        this.setState({
            order: HistoryStore.getOrder(this.props.orderId)
        });
    },

    _getVenueOutput(order) {
        var address = '';
        if (order.address == null && order.venue_id != '' && order.venue_id != null) {
            var venue = VenuesStore.getVenue(order.venue_id);
            if (venue != null) {
                address = <div>
                    <div>{venue.title}</div>
                    <div style={{fontSize: 12}}>{venue.address}</div>
                </div>;
            }
        } else {
            if (order.address != null) {
                address = order.address.formatted_address;
            }
        }
        return <div style={{display: 'table', padding: '12px'}}>
            <FontIcon style={{display: 'table-cell', verticalAlign: 'middle'}}
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
        var order = this.state.order;
        if (order != null) {
            return <Paper>
                <div style={{padding: '12px'}}>
                    Заказ <span style={{color: settings.primaryColor, fontWeight: 500}}>#{order.number}</span>
                    <div style={{float: 'right'}}>
                        <span style={{fontWeight: 500}}>{HistoryStore.getStatus(order.status)}</span>
                    </div>
                </div>
                <Divider/>
                <div>
                    {order.items.map((item, i) => {
                        return <HistoryOrderItem key={i} item={item} />;
                    })}
                </div>
                <Divider/>
                <div style={{padding: '12px', textAlign: 'right'}}>
                    <div>Итого: {order.total}р.</div>
                    <div style={{fontSize: 12}}>{PaymentsStore.getTitle(order.payment_type_id)}</div>
                </div>
                <Divider/>
                <div style={{padding: '12px'}}>
                    Готов к {order.delivery_time_str}
                </div>
                <Divider/>
                {this._getVenueOutput(order)}
            </Paper>;
        } else {
            return <div style={{textAlign: 'center', paddingTop: 12}}>
                <CircularProgress/>
            </div>;
        }
    },

    componentDidMount() {
        HistoryStore.addChangeListener(this._onHistoryStoreChange);
    },

    componentWillUnmount() {
        HistoryStore.removeChangeListener(this._onHistoryStoreChange);
    },

    render() {
        return <div style={{padding: '64px 0 0 0'}}>
            {this.getOrder()}
        </div>;
    }
});

export default HistoryOrderScreen;