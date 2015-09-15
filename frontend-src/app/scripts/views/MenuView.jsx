import React from 'react';
import { Toolbar, MenuScreen, NavigationDrawer } from '../components'

const MenuView = React.createClass({
    render() {
        return (
            <div>
                <Toolbar title='Меню' />
                <MenuScreen />
                <NavigationDrawer />
            </div>
        );
    }
});
export default MenuView;