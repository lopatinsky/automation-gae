import React from 'react';
import { Card, CardText, FlatButton, CardMedia } from 'material-ui';
import { OrderStore } from '../../stores';

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

    render() {
        var item = this.props.item;
        var width;
        var picCard;
        if (item.pic != null && item.pic != '') {
            width = '60%';
            picCard = <div style={{display: 'table-cell', width: '20%'}}>
                <CardMedia>
                    <img src={item.pic}/>
                </CardMedia>
            </div>;
        } else {
            width = '80%';
            picCard = <div/>;
        }
        alert(width);
        return (
            <Card style={{margin: '12px 12px 0 12px', display: 'table', tableLayout: 'fixed', width: '93%'}}>
                {picCard}
                <div style={{display: 'table-cell', width: width}}>
                    <CardText>
                        {item.title}
                        {this.props.gift ? ' В подарок!' : ''}
                        {this._getGroupModifiers(item)}
                        {this._getSingleModifiers(item)}
                    </CardText>
                </div>
                <div style={{display: 'table-cell', width: '20%'}}>
                    <CardText style={{textAlign: 'right', margin: '0 12px 0 0'}}>
                        {'x' + item.quantity}
                    </CardText>
                    {this.props.gift ? '' :
                        <FlatButton
                            style={{margin: '0 12px 12px 0'}}
                            label='Удалить'
                            onClick={this._removeItem}/>}

                </div>
            </Card>
        );
    }
});

export default OrderMenuItem;