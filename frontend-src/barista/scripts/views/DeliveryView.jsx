import React from 'react';
import { OrderCard } from '../components';

const DeliveryView = React.createClass({
    render() {
        const orders = this.props.delivery.map(order => <OrderCard key={order.id} order={order}/>);
        return <div>
            {orders}
        </div>;
    }
});
export default DeliveryView;
