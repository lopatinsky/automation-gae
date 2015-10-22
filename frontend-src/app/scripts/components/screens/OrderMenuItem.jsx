import React from 'react';
import { Card, CardText, FlatButton, CardMedia, IconButton } from 'material-ui';
import { OrderStore } from '../../stores';
import settings from '../../settings';

const OrderMenuItem = React.createClass({
    _removeItem() {
        OrderStore.removeItem(this.props.item);
    },

    _getGroupModifiers(item) {
        return item.group_modifiers.map(modifier => {
            return <div>
                {modifier.chosen_choice.title}
            </div>;
        });
    },

    _getSingleModifiers(item) {
        return item.single_modifiers.map(modifier => {
            if (modifier.quantity > 0) {
                return <div>
                    {modifier.title + ' x ' + modifier.quantity}
                </div>;
            }
        });
    },

    _getDeleteButton() {
         //return <FlatButton
         //   style={{margin: '0 12px 12px 0'}}
         //   label='Удалить'
         //   onClick={this._removeItem}/>;
        return <IconButton
                    onClick={this._removeItem}
                    iconClassName="material-icons"
                    iconStyle={{color: settings.primaryColor}}>
            delete
        </IconButton>;
    },

    render() {
        var item = this.props.item;
        var width;
        var picCard;
        if (item.pic != null && item.pic != '') {
            width = '55%';
            picCard = <div style={{display: 'table-cell', width: '30%'}}>
                <CardMedia>
                    <img src={item.pic}/>
                </CardMedia>
            </div>;
        } else {
            width = '85%';
            picCard = <div/>;
        }
        return (
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '12px 12px 0 12px', tableLayout: 'fixed'}}>
                    {picCard}
                    <div style={{display: 'table-cell', padding: '12px', width: width, verticalAlign: 'middle'}}>
                        <div style={{lineHeight: '120%'}}>
                            <b>{item.title + (this.props.gift ? ' В подарок!' : '')}</b>
                        </div>
                        <div style={{lineHeight: '120%'}}>
                            {this._getGroupModifiers(item)}
                            {this._getSingleModifiers(item)}
                        </div>
                    </div>
                    <div style={{display: 'table-cell', width: '15%', verticalAlign: 'middle'}}>
                        <div style={{display: 'table'}}>
                            <div style={{display: 'table-cell', verticalAlign: 'middle'}}>
                                <b>{'x' + item.quantity}</b>
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