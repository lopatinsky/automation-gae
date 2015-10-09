import React from 'react';
import { Card, CardText, FlatButton, CardMedia } from 'material-ui';
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
        e.stopPropagation();
        OrderStore.addItem(this.props.item);
    },

    render() {
        var item = this.props.item;
        return (
            <Card
                style={{padding:'0 12px 12px', display: 'table', width: '100%'}}
                onClick={this._onMenuItemTap}>
                <CardMedia
                    style={{display: 'table-cell'}}>
                    <img src={item.pic}/>
                </CardMedia>
                <div style={{display: 'table', width: '100%'}}>
                    <CardText style={{display: 'table-cell'}}>
                        {item.title}
                    </CardText>
                    <FlatButton
                        style={{display: 'table-cell'}}
                        label={item.price}
                        onClick={this._addItem} />
                </div>
            </Card>
        );
    }
});

export default MenuItem;