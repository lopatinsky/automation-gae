import React from 'react';
import { Card, CardText } from 'material-ui';
import { HistoryStore } from '../stores';
import Actions from '../Actions';

const HistoryScreen = React.createClass({
    _refresh() {
        this.setState({});
    },

    getOrders() {
        var orders = HistoryStore.getOrders();
        return orders.map(order => {
            return <Card>
                <CardText>
                    {order.number}
                </CardText>
            </Card>
        })
    },

    componentDidMount() {
        HistoryStore.addChangeListener(this._refresh);
        Actions.loadHistory();
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