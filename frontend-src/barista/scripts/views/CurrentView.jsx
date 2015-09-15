import React from 'react';
import { OrderCard } from '../components';

const CurrentView = React.createClass({
    render() {
        const orders = this.props.orderAhead.map(order => <OrderCard key={order.id} order={order}/>);
        return <div style={{overflow: 'hidden'}}>
            {orders}
        </div>;
    }
});
export default CurrentView;
