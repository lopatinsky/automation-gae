import React from 'react';
import { Toolbar } from '../components';
import { MenuItemScreen } from '../components/screens';
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
                <Toolbar title={item.title} view={this} right='order' back={true} />
                <MenuItemScreen item={item} />
            </div>
        );
    }
});
export default MenuItemView;