import React from 'react';
import { LeftNav } from 'material-ui';

const NavigationDrawer = React.createClass({
    toggle() {
        this.refs.leftNav.toggle();
    },

    _leftNavItems() {
        return [{
                route: 'menu',
                text: 'Меню'
            }, {
                route: 'order',
                text: 'Мой заказ'
            }, {
                route: 'venues',
                text: 'Кофейни'
            }, {
                route: 'history',
                text: 'История'
            }
        ];
    },

    render() {
        return <LeftNav ref="leftNav" docked={false} menuItems={this._leftNavItems()} />;
    }
});
export default NavigationDrawer;