import React from 'react';
import { Toolbar, NavigationDrawer } from '../components';
import { MenuScreen } from '../components/screens';
import { MenuStore } from '../stores';

const MenuView = React.createClass({
    toolbarLeftTap() {
        if (MenuStore.canUndoCategories()) {
            MenuStore.undoCategories()
        } else {
            this.refs.navigationDrawer.toggle();
        }
    },
    render() {
        return (
            <div>
                <Toolbar
                    title='Меню'
                    view={this}
                    right='order'/>
                <MenuScreen />
                <NavigationDrawer ref="navigationDrawer"/>
            </div>
        );
    }
});
export default MenuView;