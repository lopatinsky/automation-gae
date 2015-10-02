import React from 'react';
import { OrderList } from '../components';

const DeliveryView = React.createClass({
    render() {
        let { delivery: orders, ...other } = this.props;
        return <OrderList orders={orders} {...other}/>;
    }
});
export default DeliveryView;
