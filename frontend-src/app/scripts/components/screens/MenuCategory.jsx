import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { MenuStore } from '../../stores';
import { Navigation } from 'react-router';

const MenuCategory = React.createClass({
    mixins: [Navigation],

    _onMenuCategoryTap() {
        MenuStore.nextCategories(this.props.categories);
        MenuStore.setSelected(this.props.category.info.category_id);
    },

    render() {
        var category = this.props.category;
        return (
            <Card
                style={{margin:'0 12px 12px'}}
                onClick={this._onMenuCategoryTap}>
                <CardText>
                    {category.info.title}
                </CardText>
            </Card>
        );
    }
});

export default MenuCategory;