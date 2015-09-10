import React from 'react';
import { Tabs, Tab, List, ListItem, Avatar } from 'material-ui';
import { MenuStore } from '../stores';

const MenuScreen = React.createClass({

    _getItems(items) {
        return items.map(function(item) {
            return (
                <ListItem
                    primaryText={item.title}
                    secondaryText={item.description}
                    leftAvatar={<Avatar src={item.pic}/>}
                    rightAvatar={<Avatar>{item.price}</Avatar>}/>
            );
        });
    },

    render() {
        var categories = MenuStore.getCategories().map(function(category) {
            return (
                <Tab label={ category.info.title }>
                    <List>
                        {this._getItems(MenuStore.getItems(category))}
                    </List>
                </Tab>
            );
        });
        return (
            <Tabs>
                {categories}
            </Tabs>
        );
    }
});

export default MenuScreen;