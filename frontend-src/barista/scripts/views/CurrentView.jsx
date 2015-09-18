import React from 'react';
import { OrderCard } from '../components';

const CurrentView = React.createClass({
    render() {
        const actions = {};
        for (let [key, value] of Object.entries(this.props)) {
            if (key.substring(0, 10) == "onTouchTap") {
                actions[key] = value;
            }
        }
        const orders = this.props.orderAhead.map(
                order => <OrderCard key={order.id}
                                    order={order}
                                    {...actions}/>
        );
        return <div style={{overflow: 'hidden'}}>
            {orders}
        </div>;
    }
});
export default CurrentView;
