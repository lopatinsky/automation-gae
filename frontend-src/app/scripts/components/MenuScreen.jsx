import React from 'react';
import { Tabs, Tab, List, ListItem, Avatar } from 'material-ui';

const MenuScreen = React.createClass({
    render() {
        var categories_objs = [
            {
                name: 'First'
            },
            {
                name: 'Second'
            },
            {
                name: 'Third'
            },
            {
                name: 'Fourth'
            }
        ];
        var items_obj = [
            {
                name: 'First product',
                description: 'Big big Description for this first product',
                image: "http://lorempixel.com/600/337/nature/",
                price: 100
            },
            {
                name: 'Second product',
                description: 'Big big Description for this second product',
                image: "http://lorempixel.com/600/337/nature/",
                price: 200
            }
        ];
        var items = items_obj.map(function(item) {
            return (
                <ListItem
                    primaryText={item.name}
                    secondaryText={item.description}
                    leftAvatar={<Avatar src={item.image}/>}
                    rightAvatar={<Avatar>{item.price}</Avatar>}/>
            );
        });
        var categories = categories_objs.map(function(category) {
            return (
                <Tab label={ category.name }>
                    <List>
                        {items}
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