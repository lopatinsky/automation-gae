import React from 'react';
import { Toolbar, NavigationDrawer } from '../components';
import { OrderScreen } from '../components/screens';

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