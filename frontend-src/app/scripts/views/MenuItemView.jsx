import React from 'react';
import { Toolbar } from '../components';
import { MenuItemScreen } from '../components/screens';
import { MenuStore } from '../stores';

const MenuItemView = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    toolbarLeftTap() {
        this.context.router.goBack();
    },

    componentDidMount() {
        var item = MenuStore.itemsById[this.props.params.item_id];
        if (item == null) {
            this.context.router.goBack();
        }
    },

    render() {
        var item = MenuStore.itemsById[this.props.params.item_id];
        if (item == null) {
            return <div/>;
        }
        return (
            <div>
                <Toolbar title={item.title} view={this} right='order' back={true} />
                <MenuItemScreen item={item}/>
            </div>
        );
    }
});
export default MenuItemView;
