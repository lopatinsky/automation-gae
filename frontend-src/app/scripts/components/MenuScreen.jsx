import React from 'react';
import { Tabs, Tab, RefreshIndicator } from 'material-ui';
import { Navigation } from 'react-router';
import { MenuStore } from '../stores';
import { MenuItem, MenuCategory } from '../components';
import Actions from '../Actions';

const MenuScreen = React.createClass({
    mixins: [Navigation],

    _getItems(category) {
        if (category.categories.length > 0) {
            return category.categories.map(inner_category => {
                return (
                    <MenuCategory category={inner_category} categories={category.categories} />
                );
            });
        } else {
            return category.items.map(item => {
                return (
                    <MenuItem item={item} category={category} />
                );
            });
        }
    },

    _refresh() {
        this.setState({});
    },

    componentDidMount() {
        MenuStore.addChangeListener(this._refresh);
        if (MenuStore.getCategories() == null) {
            Actions.load();
        }
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
                        {this._getItems(category)}
                    </Tab>
                );
            });
            return (
                <Tabs
                    tabItemContainerStyle={{overflow: 'scroll', position: 'fixed', height: '32px', padding: '64px 0 0 0', zIndex: '1'}}
                    contentContainerStyle={{padding: '120px 0 0 0'}}>
                    {categories}
                </Tabs>
            );
        } else {
            return <RefreshIndicator size={40} left={80} top={5} status="loading" />
        }
    }
});

export default MenuScreen;