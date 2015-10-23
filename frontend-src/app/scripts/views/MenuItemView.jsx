import React from 'react';
import { Toolbar } from '../components';
import { MenuItemScreen } from '../components/screens';
import { MenuStore, MenuItemStore } from '../stores';
import { Navigation } from 'react-router';

const MenuItemView = React.createClass({
    mixins: [Navigation],

    toolbarLeftTap() {
        this.transitionTo('menu');
    },

    componentDidMount() {
        var item = MenuStore.getItem(this.props.params.category_id, this.props.params.item_id);
        if (item == null) {
            this.transitionTo('menu');
        }
    },

    render() {
        var item = MenuStore.getItem(this.props.params.category_id, this.props.params.item_id);
        if (item == null) {
            return <div/>;
        }
        return (
            <div>
                <Toolbar title={this.state.item.title} view={this} right='order' back={true} />
                <MenuItemScreen/>
            </div>
        );
    }
});
export default MenuItemView;