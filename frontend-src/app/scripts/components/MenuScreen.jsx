import React from 'react';
import { Tabs, Tab, List, ListItem, Avatar } from 'material-ui';
import { Navigation } from 'react-router';
import { MenuStore } from '../stores';
import Actions from '../Actions';

const MenuScreen = React.createClass({
    mixins: [Navigation],

    _getItems(category) {
        return category.items.map(item => {
            return (
                <ListItem
                    primaryText={item.title}
                    secondaryText={item.description}
                    leftAvatar={<Avatar src={item.pic}/>}
                    rightAvatar={<Avatar>{item.price}</Avatar>}
                    onClick={() => this._onMenuItemTap(category, item)}/>
            );
        });
    },

    _refresh() {
        this.setState({ load: true});
    },

    _onMenuItemTap(category, item) {
        Actions.setMenuItem(item);
        this.transitionTo('menu_item', {category_id: category.info.category_id, item_id: item.id });
    },

    getInitialState: function() {
        return { load: false};
    },

    componentDidMount() {
        MenuStore.addChangeListener(this._refresh);
        Actions.loadMenu();
    },

    componentWillUnmount() {
        MenuStore.removeChangeListener(this._refresh);
    },

    render() {
        if (MenuStore.getCategories() != null) {
            var categories = MenuStore.getCategories().map((category) => {
                return (
                    <Tab
                        label={category.info.title}>
                        <List>
                            {this._getItems(category)}
                        </List>
                    </Tab>
                );
            });
            return (
                <Tabs>
                    {categories}
                </Tabs>
            );
        } else {
            return <p>Меню еще не загрузилось</p>
        }
    }
});

export default MenuScreen;