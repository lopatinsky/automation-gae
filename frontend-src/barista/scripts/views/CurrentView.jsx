import React from 'react';
import { OrderStore } from '../stores';
import { OrderCard } from '../components';

const CurrentView = React.createClass({
    _onOrderStoreChange() {
        this.setState({
            orders: OrderStore.getOrderAheadOrders()
        });
    },
    getInitialState() {
        return {
            orders: OrderStore.getOrderAheadOrders()
        }
    },
    componentDidMount() {
        OrderStore.addChangeListener(this._onOrderStoreChange);
    },
    componentWillUnmount() {
        OrderStore.removeChangeListener(this._onOrderStoreChange);
    },
    render() {
        const orders = this.state.orders.map(order => <OrderCard key={order.id} order={order}/>);
        return <div>
            {orders}
        </div>;
    }
});
export default CurrentView;
