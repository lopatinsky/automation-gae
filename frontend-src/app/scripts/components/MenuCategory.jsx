import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { MenuStore, OrderStore } from '../stores';
import { Navigation } from 'react-router';
import Actions from '../Actions';

const MenuCategory = React.createClass({
    mixins: [Navigation],

    _onMenuCategoryTap() {
        MenuStore.nextCategories(this.props.categories);
    },

    render() {
        var category = this.props.category;
        return (
            <Card onClick={this._onMenuCategoryTap}>
                <CardText>
                    {category.info.title}
                </CardText>
            </Card>
        );
    }
});

export default MenuCategory;