import React from 'react';
import { Card, CardText } from 'material-ui';

const OrderCard = React.createClass({
    _modifierStr(mod) {
        return mod.quantity > 1 ? `${mod.name} x${mod.quantity}` : mod.name;
    },
    _renderItem(item, index, array) {
        const modifiers = [];
        for (let mod of item.group_modifiers) {
            modifiers.push(this._modifierStr(mod));
        }
        for (let mod of item.single_modifiers) {
            modifiers.push(this._modifierStr(mod));
        }
        return <tr key={index}>
            <td style={{padding: 0}}>
                {array == this.props.order.gifts && <span style={{fontWeight: 500}}>Подарок! </span>}
                {item.title} {modifiers.length && <span>({modifiers.join(', ')})</span>}
            </td>
            <td style={{fontWeight: 500, padding: 0, width: 1}}>
                x{item.quantity}
            </td>
        </tr>;
    },
    render() {
        const cellStyle = {
                display: 'table-cell',
                verticalAlign: 'top'
            },
            lightStyle = {
                fontWeight: 300
            },
            boldStyle= {
                fontWeight: 500
            },
            order = this.props.order,
            items = order.items.map(this._renderItem),
            gifts = order.gifts.map(this._renderItem);
        return <Card style={{margin:'0 12px 12px'}}>
            <CardText>
                <div style={{display: 'table', width:'100%', marginBottom: 6}}>
                    <div style={{...lightStyle, ...cellStyle}}>
                        <div>#{order.number}</div>
                        <div>{order.statusName}</div>
                    </div>
                    <div style={cellStyle}>
                        <div>{order.deliveryTime.format('H:mm')}</div>
                        <div style={lightStyle}>{order.deliveryTime.format('D MMM')}</div>
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
                            <div>
                                {order.paymentTypeName}:{' '}
                                <span style={boldStyle}>{order.paymentSum} р.</span>
                            </div>
                            {order.walletPayment > 0 && <div style={lightStyle}>Оплата баллами: {order.walletPayment} р.</div>}
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
