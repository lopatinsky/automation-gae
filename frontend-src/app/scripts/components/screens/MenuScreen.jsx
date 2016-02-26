import React from 'react';
import { Tabs, Tab, RefreshIndicator, DropDownMenu, Card, Paper } from 'material-ui';
import { MenuStore } from '../../stores';
import MenuItem from './MenuItem';
import MenuCategory from './MenuCategory';

const MenuScreen = React.createClass({
    _getItems(category) {
        if (category.categories.length > 0) {
            return category.categories.map(inner_category => {
                return (
                    <MenuCategory key={inner_category.info.category_id} category={inner_category}/>
                );
            });
        } else {
            return category.items.map(item => {
                return (
                    <MenuItem key={item.id} item={item} category={category} />
                );
            });
        }
    },

    _onCategoryTap(e, selectedIndex, menuItem) {
        MenuStore.setSelected(menuItem.category_id);
    },

    _getCategoryList(categories) {
        var categories = categories.map((category) => {
           return <MenuCategory key={category.info.category_id} category={category} categories={[category]} />;
        });
        return <div style={{paddingTop: '76px'}}>
            {categories}
        </div>;
    },

    _getCategoryPicker(categories) {
        var menuItems = categories.map(category => {
            return {category_id: category.info.category_id, text: category.info.title};
        });
        var categoryId = this.props.category;
        if (categoryId == null) {
            categoryId = MenuStore.getCategories()[0].info.category_id;
        }
        var category = MenuStore.categoriesById[categoryId];
        return <div>
            <div style={{position: 'fixed', marginTop: '64px', zIndex: '9', width: '100%'}}>
                <Paper>
                    <DropDownMenu
                        style={{zIndex: '10', width: '100%'}}
                        underlineStyle={{display: 'none'}}
                        menuItems={menuItems}
                        selectedIndex={MenuStore.getSelectedIndex()}
                        onChange={this._onCategoryTap}/>
                </Paper>
            </div>
            <div style={{padding: '132px 0 0 0'}}>
                {this._getItems(category)}
            </div>
        </div>;
    },

    _getTabs(categories) {
        var categories = categories.map((category) => {
            return (
                <Tab key={category.info.category_id}
                     value={category.info.category_id}
                     label={<div style={{padding: '0 6px 0 6px'}}>{category.info.title}</div>}>
                    {this._getItems(category)}
                </Tab>
            );
        });
        return (
            <Tabs
                value={this.props.category_id}
                tabItemContainerStyle={{position: 'fixed', overflow: 'auto', zIndex: '3', padding: '64px 0 0 0'}}
                contentContainerStyle={{padding: '120px 0 0 0'}}>
                {categories}
            </Tabs>
        );
    },

    _refresh() {
        window.scrollTo(0, 0);
        this.setState({});
    },

    componentDidMount() {
        MenuStore.addChangeListener(this._refresh);
        this._refresh();
    },

    componentWillUnmount() {
        MenuStore.removeChangeListener(this._refresh);
    },

    render() {
        let menu;
        let categories;
        if (MenuStore.rootCategories.length && this.props.category) {
            const cat = MenuStore.categoriesById[this.props.category];
            if (cat.categories.length) {
                categories = cat.categories;
            } else {
                categories = [cat];
            }
        } else {
            categories = MenuStore.rootCategories;
        }
        if (categories.length) {
            if (categories.length < 5) {
                menu = this._getTabs(categories);
            } else if (categories.length < 9) {
                menu = this._getCategoryPicker(categories);
            } else {
                menu = this._getCategoryList(categories);
            }
        }
        return <div>
            {menu}
        </div>;
    }
});

export default MenuScreen;