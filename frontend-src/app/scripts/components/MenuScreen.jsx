import React from 'react';
import { Tabs, Tab, RefreshIndicator, DropDownMenu, Card, Paper } from 'material-ui';
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

    _onCategoryTap(e, selectedIndex, menuItem) {
        MenuStore.setSelected(menuItem.category_id);
    },

    _getCategoryPicker() {
        var menuItems = MenuStore.getCategories().map(category => {
            return {category_id: category.info.category_id, text: category.info.title};
        });
        var categoryId = MenuStore.getSelected();
        if (categoryId == null) {
            categoryId = MenuStore.getCategories()[0].info.category_id;
        }
        var category = MenuStore.getCategory(categoryId);
        return <div>
            <Paper style={{position: 'fixed', margin: '76px 12px 0 12px', zIndex: '9', width: '93%'}}>
                <DropDownMenu
                    style={{zIndex: '10', width: '100%'}}
                    underlineStyle={{display: 'none'}}
                    menuItems={menuItems}
                    selectedIndex={MenuStore.getSelectedIndex()}
                    onChange={this._onCategoryTap}/>
            </Paper>
            <div style={{padding: '144px 0 0 0'}}  >
                {this._getItems(category)}
            </div>
        </div>;
    },

    _getTabs() {
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
            if (MenuStore.getCategories().length < 5) {
                return this._getTabs();
            } else {
                return this._getCategoryPicker();
            }
        } else {
            return <RefreshIndicator size={40} left={80} top={5} status="loading" />
        }
    }
});

export default MenuScreen;