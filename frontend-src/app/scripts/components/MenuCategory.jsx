import React from 'react';
import { Tab } from 'material-ui';
import { MenuItem } from '../components'

const MenuCategory = React.createClass({
    render() {
        var items_obj = [
            {
                name: 'First product',
                description: 'Big big Description for this first product',
                image: "http://lorempixel.com/600/337/nature/"
            },
            {
                name: 'Second product',
                description: 'Big big Description for this second product',
                image: "http://lorempixel.com/600/337/nature/"
            }
        ];
        var items = items_obj.map(function(item) {
            return (
                <MenuItem item={item}/>
            );
        });
        return (
            <Tab label={ this.props.category.name }>
                {items}
            </Tab>
        );
    }
});

export default MenuCategory;