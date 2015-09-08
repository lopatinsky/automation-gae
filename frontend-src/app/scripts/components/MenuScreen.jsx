import React from 'react';
import { Tabs, Tab } from 'material-ui';

const MenuScreen = React.createClass({
    render() {
        var category_names = ["Первая", "Вторая", "Третья"];
        var categories = category_names.map(function(name) {
            return (
                <Tab label={ name }>
                    Контент
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