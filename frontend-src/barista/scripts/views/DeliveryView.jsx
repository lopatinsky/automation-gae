import React from 'react';
import { OrderCard } from '../components';

const DeliveryView = React.createClass({
    render() {
        const actions = {};
        for (let [key, value] of Object.entries(this.props)) {
            if (key.substring(0, 10) == "onTouchTap") {
                actions[key] = value;
            }
        }
        const orders = this.props.delivery.map(
                order => <OrderCard key={order.id}
                                    order={order}
                                    {...actions}/>
        );
        return <div style={{overflow: "hidden"}}>
            {orders}
        </div>;
    }
});
export default DeliveryView;
