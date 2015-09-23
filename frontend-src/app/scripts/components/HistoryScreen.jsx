import React from 'react';
import { Card, CardText } from 'material-ui';
import { HistoryStore } from '../stores';
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
            return <Card onClick={() => this._onOrderTap(order)}>
                <CardText>
                    {order.number}
                </CardText>
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
        return <div>
            {this.getOrders()}
        </div>;
    }
});

export default HistoryScreen;