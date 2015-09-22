import React from 'react';
import { OrderList } from '../components';

const CurrentView = React.createClass({
    render() {
        let { orderAhead: orders, ...other } = this.props;
        return <OrderList orders={orders} {...other}/>;
    }
});
export default CurrentView;
