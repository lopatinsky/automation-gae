import React from 'react';
import { Toolbar, MenuItemScreen } from '../components';
import { MenuStore } from '../stores';

const MenuItemView = React.createClass({
    render() {
        var item = MenuStore.getItem(this.props.params.category_id, this.props.params.item_id);
        return (
            <div>
                <Toolbar title={item.title} />
                <MenuItemScreen item={item} />
            </div>
        );
    }
});
export default MenuItemView;