import React from 'react';
import { LeftNav, FontIcon, MenuItem } from 'material-ui';
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
    contextTypes: {
        router: React.PropTypes.object.isRequired,
        location: React.PropTypes.object.isRequired
    },

    toggle() {
        this.setState({
            index: INDEXES[this.context.location.pathname],
            open: ! this.state.open
        });
    },

    _onItemTouchTap(route) {
        this.context.router.replace(route);
        setImmediate(() => this.toggle());
    },

    _getItem(title, route, icon_name, index) {
        let icon = <FontIcon style={{display: 'table-cell', width: '10%', verticalAlign: 'middle', fontSize: '20px'}}
                             color={index == this.state.index ? settings.primaryColor : Colors.grey500}
                             className="material-icons">
            {icon_name}
        </FontIcon>;
        return <MenuItem key={index}
                         leftIcon={icon}
                         onTouchTap={() => this._onItemTouchTap(route)}>
            {title}
        </MenuItem>;
    },

    _leftNavItems() {
        return [
            this._getItem('Меню', '/', 'restaurant_menu', 0),
            this._getItem('Заказ', '/order', 'shopping_basket', 1),
            this._getItem('Адреса', '/venues', 'place', 2),
            this._getItem('История', '/history', 'history', 3),
            this._getItem('Акции', '/promos', 'loyalty', 4),
            this._getItem('Настройки', '/settings', 'settings', 5)
        ];
    },

    getInitialState() {
        return {
            index: 0,
            open: false
        };
    },

    _onRequestChange(wantedState) {
        this.setState({
            open: wantedState
        })
    },

    render() {
        return <LeftNav open={this.state.open}
                        disableSwipeToOpen={true}
                        docked={false}
                        onRequestChange={this._onRequestChange}
                        ref="leftNav">
            {this._leftNavItems()}
        </LeftNav>;
    }
});
export default NavigationDrawer;
