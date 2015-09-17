import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { OrderStore } from '../stores';
import { Navigation } from 'react-router';
import Actions from '../Actions';

const MenuItem = React.createClass({
    mixins: [Navigation],

    _onMenuItemTap() {
        Actions.setMenuItem(this.props.item);
        this.transitionTo('menu_item', {
            category_id: this.props.category.info.category_id,
            item_id: this.props.item.id
        });
    },

    _addItem(e) {
        e.preventDefault();
        OrderStore.addItem(this.props.item, this.props.item.price);
    },

    render() {
        var item = this.props.item;
        return (
            <Card onClick={this._onMenuItemTap}>
                <CardText>
                    {item.title}
                </CardText>
                <FlatButton label={item.price} onClick={this._addItem} />
            </Card>
        );
    }
});

export default MenuItem;