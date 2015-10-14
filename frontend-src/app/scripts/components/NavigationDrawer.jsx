import React from 'react';
import { LeftNav } from 'material-ui';
import { Navigation } from 'react-router';
import Router from 'react-router';

var INDEXES = {
    '/': 0, // menu
    '/order': 1,
    '/venues': 2,
    '/history': 3,
    '/promos':4,
    '/settings': 5
};

const NavigationDrawer = React.createClass({
    mixins: [Navigation, Router.State],

    _selectMenuItem(e, selectedIndex, menuItem) {
        this.transitionTo(menuItem.route);
    },

    toggle() {
        this.setState({
            index: INDEXES[this.getPathname()]
        });
        this.refs.leftNav.toggle();
    },

    _leftNavItems() {
        return [{
                index: 0,
                route: 'menu',
                text: 'Меню'
            }, {
                index: 1,
                route: 'order',
                text: 'Мой заказ'
            }, {
                index: 2,
                route: 'venues',
                text: 'Кофейни'
            }, {
                index: 3,
                route: 'history',
                text: 'История'
            }, {
                index: 4,
                route: 'promos',
                text: 'Акции'
            }, {
                index: 5,
                route: 'settings',
                text: 'Настройки'
            }
        ];
    },

    getInitialState() {
        return {
            index: 0
        };
    },

    render() {
        return <LeftNav
            selectedIndex={this.state.index}
            ref="leftNav"
            docked={false}
            menuItems={this._leftNavItems()}
            onChange={this._selectMenuItem}/>;
    }
});
export default NavigationDrawer;