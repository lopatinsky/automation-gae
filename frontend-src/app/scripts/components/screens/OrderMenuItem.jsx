import React from 'react';
import { Card, CardText, FlatButton, CardMedia, IconButton } from 'material-ui';
import settings from '../../settings';
import { AppActions } from '../../actions';

const OrderMenuItem = React.createClass({
    _removeItem() {
        AppActions.removeItem(this.props.item);
    },

    _getGroupModifiers(orderItem) {
        const result = [];
        for (const gm of orderItem.item.group_modifiers) {
            const choice = orderItem.groupModifiers[gm.modifier_id];
            if (choice) {
                result.push(<div key={gm.modifier_id}>
                    {choice.title}
                </div>);
            }
        }
        return result;
    },

    _getSingleModifiers(orderItem) {
        const result = [];
        for (const sm of orderItem.item.single_modifiers) {
            const quantity = orderItem.singleModifiers[sm.modifier_id];
            if (quantity) {
                result.push(<div key={sm.modifier_id}>
                    {modifier.title} x{modifier.quantity}
                </div>);
            }
        }
        return result;
    },

    _getDeleteButton() {
        return <IconButton
                    onTouchTap={this._removeItem}
                    iconClassName="material-icons"
                    iconStyle={{color: settings.primaryColor}}>
            delete
        </IconButton>;
    },

    render() {
        var orderItem = this.props.item,
            item = orderItem.item;
        var width;
        var picCard;
        if (item.pic != null && item.pic != '') {
            width = '55%';
            picCard = <div style={{display: 'table-cell', width: '30%', verticalAlign: 'middle'}}>
                <CardMedia>
                    <img src={item.pic}/>
                </CardMedia>
            </div>;
        } else {
            width = '85%';
            picCard = null;
        }
        return (
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '12px 12px 0 12px', tableLayout: 'fixed'}}>
                    {picCard}
                    <div style={{display: 'table-cell', padding: '12px', width: width, verticalAlign: 'middle'}}>
                        <div style={{lineHeight: '120%'}}>
                            {item.title + (this.props.gift ? ' (подарок)' : '')}
                        </div>
                        <div style={{lineHeight: '120%'}}>
                            {this._getGroupModifiers(orderItem)}
                            {this._getSingleModifiers(orderItem)}
                        </div>
                    </div>
                    <div style={{display: 'table-cell', width: '15%', verticalAlign: 'middle'}}>
                        <div style={{display: 'table'}}>
                            <div style={{display: 'table-cell', verticalAlign: 'middle'}}>
                                {'x' + orderItem.quantity}
                            </div>
                            <div style={{display: 'table-cell', verticalAlign: 'middle'}}>
                                {this.props.gift ? '' : this._getDeleteButton()}
                            </div>
                        </div>
                    </div>
                </Card>
            </div>
        );
    }
});

export default OrderMenuItem;