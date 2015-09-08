import React from 'react';
import { Tabs } from 'material-ui';
import { MenuCategory } from '../components'

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
            }
        ];
        var categories = categories_objs.map(function(category) {
            return <MenuCategory category={category} />
        });
        return (
            <Tabs>
                {categories}
            </Tabs>
        );
    }
});

export default MenuScreen;