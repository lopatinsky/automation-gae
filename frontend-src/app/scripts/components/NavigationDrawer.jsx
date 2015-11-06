import React from 'react';
import { LeftNav, FontIcon } from 'material-ui';
import { Navigation } from 'react-router';
import Router from 'react-router';
import settings from '../settings';
import Colors from 'material-ui/lib/styles/colors';

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

    _getItem(title, icon_name, index) {
        return <div style={{display: 'table'}}>
            <FontIcon style={{display: 'table-cell', width: '10%', verticalAlign: 'middle', fontSize: '20px'}}
                      color={index == this.state.index ? settings.primaryColor : Colors.grey500}
                      className="material-icons">
                {icon_name}
            </FontIcon>
            <div style={{display: 'table-cell', paddingLeft: '12px'}}>
                {title}
            </div>
        </div>;
    },

    _leftNavItems() {
        return [{
                index: 0,
                route: 'menu',
                text: this._getItem('Меню', 'restaurant_menu', 0)
            }, {
                index: 1,
                route: 'order',
                text: this._getItem('Заказ', 'shopping_basket', 1)
            }, {
                index: 2,
                route: 'venues',
                text: this._getItem('Адреса', 'place', 2)
            }, {
                index: 3,
                route: 'history',
                text: this._getItem('История', 'history', 3)
            }, {
                index: 4,
                route: 'promos',
                text: this._getItem('Акции', 'loyalty', 4)
            }, {
                index: 5,
                route: 'settings',
                text: this._getItem('Настройки', 'settings', 5)
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
            disableSwipeToOpen={true}
            docked={false}
            selectedIndex={this.state.index}
            ref="leftNav"
            menuItems={this._leftNavItems()}
            onChange={this._selectMenuItem}/>;
    }
});
export default NavigationDrawer;