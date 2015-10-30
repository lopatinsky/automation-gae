import React from 'react';
import { Card, CardText, FlatButton, CardMedia } from 'material-ui';
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
        var picCard = <div style={{display: 'table-cell', width: '40%'}}>
            <CardMedia>
                <img src={category.info.pic}/>
            </CardMedia>
        </div>;
        return (
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin:'0 12px 12px'}}
                      onClick={this._onMenuCategoryTap}>
                    {category.info.pic ? picCard: null}
                    <div style={{display: 'table-cell', verticalAlign: 'middle'}}>
                        <CardText>
                            {category.info.title}
                        </CardText>
                    </div>
                </Card>
            </div>
        );
    }
});

export default MenuCategory;