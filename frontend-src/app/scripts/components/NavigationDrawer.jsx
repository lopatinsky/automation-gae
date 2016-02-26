import React from 'react';
import { LeftNav, FontIcon, MenuItem } from 'material-ui';
import settings from '../settings';
import Colors from 'material-ui/lib/styles/colors';

const NavigationDrawer = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired,
        location: React.PropTypes.object.isRequired
    },

    toggle() {
        this.setState({
            open: ! this.state.open
        });
    },

    _onItemTouchTap(route) {
        this.context.router.replace(route);
        this.toggle()
    },

    _getItem(title, route, icon_name) {
        const active = this.context.router.isActive(route),
            style = active ? {color: settings.primaryColor} : {};
        let icon = <FontIcon style={{display: 'table-cell', width: '10%', verticalAlign: 'middle', ...style}}
                             className="material-icons">
            {icon_name}
        </FontIcon>;
        return <MenuItem key={route}
                         leftIcon={icon}
                         style={style}
                         onTouchTap={() => this._onItemTouchTap(route)}>
            {title}
        </MenuItem>;
    },

    _leftNavItems() {
        return [
            this._getItem('Меню', '/menu', 'restaurant_menu'),
            this._getItem('Заказ', '/order', 'shopping_basket'),
            this._getItem('Адреса', '/venues', 'place'),
            this._getItem('История', '/history', 'history'),
            this._getItem('Акции', '/promos', 'loyalty'),
            this._getItem('Настройки', '/settings', 'settings')
        ];
    },

    getInitialState() {
        return {
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
                        docked={false}
                        onRequestChange={this._onRequestChange}
                        ref="leftNav">
            {this._leftNavItems()}
        </LeftNav>;
    }
});
export default NavigationDrawer;
