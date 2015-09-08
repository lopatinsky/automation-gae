import React from 'react';
import { Tabs, Tab } from 'material-ui';

const MenuScreen = React.createClass({
    render() {
        var category_names = ["������", "������", "������"];
        var categories = category_names.map(function(name) {
            return (
                <Tab label={ name }>
                    �������
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