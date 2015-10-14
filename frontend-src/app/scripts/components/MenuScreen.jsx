import React from 'react';
import { Tabs, Tab, RefreshIndicator } from 'material-ui';
import { Navigation } from 'react-router';
import { MenuStore } from '../stores';
import { MenuItem, MenuCategory } from '../components';
import Actions from '../Actions';

const MenuScreen = React.createClass({
    mixins: [Navigation],
    value: null,

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

    _changeTab(value, e, tab) {
        this.value = value;
        MenuStore.setSelected(value);
    },

    _refresh() {
        this.setState({
            value: this.value
        });
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

    getInitialState() {
        this.value = MenuStore.getSelected();
        return {
            value: this.value
        }
    },

    render() {
        if (MenuStore.getCategories() != null) {
            var categories = MenuStore.getCategories().map((category) => {
                return (
                    <Tab
                        value={category.info.category_id}
                        label={<div style={{padding: '0 6px 0 6px', height: '32px'}}>{category.info.title}</div>}>
                        {this._getItems(category)}
                    </Tab>
                );
            });
            return (
                <Tabs
                    value={this.state.value}
                    onChange={this._changeTab}
                    tabItemContainerStyle={{position: 'fixed', overflow: 'auto', height: '32px', zIndex: '1', padding: '64px 0 0 0'}}
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