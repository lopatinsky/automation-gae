import React from 'react';
import { Toolbar, MenuScreen, NavigationDrawer } from '../components'

const MenuView = React.createClass({
    toolbarLeftTap() {
        //this.refs.navigationDrawer.toggle();
    },

    render() {
        return (
            <div>
                <Toolbar title='Меню' view={this} />
                <MenuScreen />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default MenuView;