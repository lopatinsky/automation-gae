import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { OrderStore } from '../stores';
import Actions from '../Actions';

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
        return (
            <Card>
                <CardText>
                    {item.title + ' x ' + item.quantity}
                    {this._getGroupModifiers(item)}
                    {this._getSingleModifiers(item)}
                </CardText>
                <div>
                    <FlatButton label='Удалить' onClick={this._removeItem} />
                </div>
            </Card>
        );
    }
});

export default OrderMenuItem;