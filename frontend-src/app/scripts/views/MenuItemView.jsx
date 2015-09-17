import React from 'react';
import { Toolbar, MenuItemScreen, ModifierDialog } from '../components';
import { MenuStore } from '../stores';
import { Navigation } from 'react-router';

const MenuItemView = React.createClass({
    mixins: [Navigation],

    toolbarLeftTap() {
        this.transitionTo('menu');
    },

    render() {
        var item = MenuStore.getItem(this.props.params.category_id, this.props.params.item_id);
        return (
            <div>
                <Toolbar title={item.title} view={this} right='order' />
                <MenuItemScreen item={item} />
            </div>
        );
    }
});
export default MenuItemView;