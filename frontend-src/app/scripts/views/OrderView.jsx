import React from 'react';
import { Toolbar, OrderScreen, NavigationDrawer } from '../components';

const OrderView = React.createClass({
    toolbarLeftTap() {
        this.refs.navigationDrawer.toggle();
    },

    render() {
        return (
            <div>
                <Toolbar title='Мой заказ' view={this} />
                <OrderScreen />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default OrderView;