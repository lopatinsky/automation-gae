import React from 'react';
import { Toolbar, MenuItemScreen, ModifierDialog } from '../components';
import { MenuStore } from '../stores';

const MenuItemView = React.createClass({
    toolbarLeftTap() {
        alert("left tap");
    },

    render() {
        var item = MenuStore.getItem(this.props.params.category_id, this.props.params.item_id);
        return (
            <div>
                <Toolbar title={item.title} view={this} />
                <MenuItemScreen item={item} />

            </div>
        );
    }
});
export default MenuItemView;