import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { OrderStore } from '../stores';
import Actions from '../Actions';

const OrderMenuItem = React.createClass({
    _removeItem() {
        OrderStore.removeItem(this.props.item);
    },

    render() {
        var item = this.props.item;
        return (
            <Card>
                <CardText>
                    {item.title} {' x ' + item.quantity}
                </CardText>
                <div>
                    <FlatButton label='Удалить' onClick={this._removeItem} />
                </div>
            </Card>
        );
    }
});

export default OrderMenuItem;