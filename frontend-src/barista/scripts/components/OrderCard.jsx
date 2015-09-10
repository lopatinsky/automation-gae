import React from 'react';
import { Card, CardText } from 'material-ui';

const OrderCard = React.createClass({
    _renderItem(item, index, array) {
        return <tr key={index}>
            <td style={{padding: 0}}>
                {item.title}
                {array == this.props.order.gifts && "Подарок"}
            </td>
            <td style={{padding: 0, width: 1}}>
                x{item.quantity}
            </td>
        </tr>;
    },
    render() {
        const cellStyle = {
                display: 'table-cell',
                verticalAlign: 'middle'
            },
            order = this.props.order,
            items = order.items.map(this._renderItem),
            gifts = order.gifts.map(this._renderItem);
        return <Card style={{margin:'0 12px 12px'}}>
            <CardText>
                <div style={{display: 'table', width:'100%'}}>
                    <div style={cellStyle}>
                        <div>#{order.number}</div>
                        <div>{order.statusName}</div>
                    </div>
                    <div style={cellStyle}>
                        {order.deliveryTime}
                    </div>
                    <div style={cellStyle}>
                        <div>{order.client.name}</div>
                        <div>{order.client.phone}</div>
                    </div>
                    <div style={cellStyle}>
                        <table style={{borderSpacing: 0, width: '100%'}}>
                            {items}
                            {gifts}
                        </table>
                        <div style={{textAlign: 'right'}}>
                            {order.paymentTypeName}: {order.paymentSum} р.
                        </div>
                    </div>
                </div>
                {order.comment && <div>Комментарий клиента: {order.comment}</div>}
                <div>{order.deliveryTypeName}</div>
            </CardText>
        </Card>
    }
});
export default OrderCard;
