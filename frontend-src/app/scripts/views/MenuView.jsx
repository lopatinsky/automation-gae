import React from 'react';
import { Toolbar } from '../components';
import { MenuScreen } from '../components/screens';
import { MenuStore } from '../stores';

const MenuView = React.createClass({
    toolbarLeftTap() {
        if (MenuStore.canUndoCategories()) {
            MenuStore.undoCategories()
        } else {
            this.props.getDrawer().toggle();
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
            </div>
        );
    }
});
export default MenuView;