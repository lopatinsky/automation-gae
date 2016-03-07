import React from 'react';
import FontIcon from 'material-ui/lib/font-icon';
import Paper from 'material-ui/lib/paper';
import { HistoryStore, VenuesStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { LoadingDialog } from '../dialogs'
import settings from '../../settings';

const HistoryScreen = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _onOrderTap(order) {
        this.context.router.push(`/order/${order.order_id}`);
    },

    getOrders() {
        var orders = HistoryStore.getOrders();
        if (orders.length == 0) {
            return <div style={{textAlign: 'center'}}>
                История заказов пуста
            </div>;
        }
        return orders.map(order => {
            var from_title = '';
            if (order.delivery_type == 2) {
                from_title = order.address.formatted_address;
            } else {
                var venue = VenuesStore.getVenue(order.venue_id);
                if (venue != null) {
                    from_title = venue.title;
                }
            }

            return <Paper key={order.order_id}
                          style={{margin: '0 12px 12px', padding: 12}} onTouchTap={() => this._onOrderTap(order)}>
                <div>
                    Мой заказ{' '}
                    <span style={{color: settings.primaryColor, fontWeight: 500}}>#{order.number}</span>
                    <div style={{float: 'right', fontWeight: 500}}>
                        {order.total} руб.
                    </div>
                </div>
                <div style={{paddingTop: 6}}>
                    {order.delivery_time_str}
                    <div style={{float: 'right'}}>
                        {HistoryStore.getStatus(order.status)}
                    </div>
                </div>
                <div style={{paddingTop: 6}}>
                    <FontIcon color={settings.primaryColor}
                              style={{verticalAlign: 'middle'}}
                              className="material-icons">
                        location_on
                    </FontIcon>
                    <span style={{paddingLeft: 6, verticalAlign: 'middle'}}>
                        {from_title}
                    </span>
                </div>
            </Paper>
        })
    },

    getInitialState() {
        let loading = HistoryStore.isLoading() && !HistoryStore.isOrderLoaded();
        return {
            loading
        };
    },

    _onHistoryStoreChanged() {
        let loading = HistoryStore.isLoading() && !HistoryStore.isOrderLoaded();
        this.setState({
            loading
        });
    },

    componentDidMount() {
        ServerRequests.loadHistory();
        HistoryStore.addChangeListener(this._onHistoryStoreChanged);
    },

    componentWillUnmount() {
        HistoryStore.removeChangeListener(this._onHistoryStoreChanged);
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this.getOrders()}
            <LoadingDialog open={this.state.loading}
                           title='Загрузка истории'/>
        </div>;
    }
});

export default HistoryScreen;