import React from 'react';
import { LeftNav } from 'material-ui';
import { Navigation } from 'react-router';

const NavigationDrawer = React.createClass({
    mixins: [Navigation],

    _selectMenuItem(e, selectedIndex, menuItem) {
        this.transitionTo(menuItem.route);
    },

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
            }, {
                route: 'promos',
                text: 'Акции'
            }, {
                route: 'settings',
                text: 'Настройки'
            }
        ];
    },

    render() {
        return <LeftNav ref="leftNav" docked={false} menuItems={this._leftNavItems()} onChange={this._selectMenuItem}/>;
    }
});
export default NavigationDrawer;