import React from 'react';
import { Card, CardText } from 'material-ui';
import { HistoryStore, VenuesStore } from '../stores';
import { Navigation } from 'react-router';
import Actions from '../Actions';

const HistoryScreen = React.createClass({
    mixins: [Navigation],

    _refresh() {
        this.setState({});
    },

    _onOrderTap(order) {
        this.transitionTo('historyOrder', {
            order_id: order.order_id
        });
    },

    getOrders() {
        var orders = HistoryStore.getOrders();
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

            return <Card
                style={{margin: '0 12px 12px 12px', display: 'table', width: '93%'}}
                onClick={() => this._onOrderTap(order)}>
                <div style={{display: 'table-cell'}}>
                    <div>
                        <b>Мой заказ #{order.number}</b>
                    </div>
                    <div>
                        {order.delivery_time_str}
                    </div>
                    <div>
                        {from_title}
                    </div>
                </div>
                <div style={{display: 'table-cell'}}>
                    <div>
                        <b>{order.total} руб.</b>
                    </div>
                    <div>
                        {HistoryStore.getStatus(order.status)}
                    </div>
                </div>
            </Card>
        })
    },

    componentDidMount() {
        Actions.loadHistory();
        HistoryStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        HistoryStore.removeChangeListener(this._refresh);
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this.getOrders()}
        </div>;
    }
});

export default HistoryScreen;