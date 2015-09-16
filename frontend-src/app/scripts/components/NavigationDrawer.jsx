import React from 'react';
import { LeftNav } from 'material-ui';

const NavigationDrawer = React.createClass({
    toggle() {
        this.refs.leftNav.toggle();
    },

    _leftNavItems() {
        return [{
                route: 'menu',
                text: '����'
            }, {
                route: 'order',
                text: '��� �����'
            }, {
                route: 'venues',
                text: '�������'
            }, {
                route: 'history',
                text: '�������'
            }
        ];
    },

    render() {
        return <LeftNav ref="leftNav" docked={false} menuItems={this._leftNavItems()} />;
    }
});
export default NavigationDrawer;