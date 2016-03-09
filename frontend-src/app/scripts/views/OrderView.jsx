import React from 'react';
import { Toolbar } from '../components';
import { OrderScreen } from '../components/screens';

const OrderView = React.createClass({
    toolbarLeftTap() {
        this.props.getDrawer().toggle();
    },

    render() {
        return (
            <div>
                <Toolbar title='Мой заказ' view={this} />
                <OrderScreen />
            </div>
        );
    }
});
export default OrderView;