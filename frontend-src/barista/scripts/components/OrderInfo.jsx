import React from 'react';
import { OrderStore } from '../stores';

const OrderInfo = React.createClass({
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
                <span style={{fontWeight: 400}}>{item.title} </span>
                {!!modifiers.length && <span>({modifiers.join(', ')})</span>}
            </td>
            <td style={{fontWeight: 500, padding: 0, width: 1}}>
                x{item.quantity}
            </td>
        </tr>;
    },
    _renderExtraData() {
        const extraData = [...this.props.order.client.extra_data, ...this.props.order.extraData];
        if (!extraData.length) {
            return null;
        }
        const elements = extraData.map(elem =>
            <div key={elem.field}>
                {elem.title}:
                <span style={{fontWeight: 400}}> {elem.value == "" || elem.value == null ? "не указано" : elem.value}</span>
            </div>);
        return <div>{elements}</div>;
    },
    render() {
        const cellStyle = {
                display: 'table-cell',
                verticalAlign: 'top'
            },
            bolderStyle = { fontWeight: 400 },
            boldStyle = { fontWeight: 500 },
            order = this.props.order,
            items = order.items.map(this._renderItem),
            gifts = order.gifts.map(this._renderItem);
        return <div>
            <div style={{display: 'table', width:'100%', marginBottom: 6}}>
                <div style={{width: '13%', ...cellStyle}}>
                    <div>#{order.number}</div>
                    <div>{order.statusName}</div>
                </div>
                <div style={{width: '8%', ...cellStyle}}>
                    <div style={bolderStyle}>{order.deliveryTime.format('H:mm')}</div>
                    <div>{order.deliveryTime.format('D MMM')}</div>
                </div>
                <div style={{width: '14%', ...bolderStyle, ...cellStyle}}>
                    <div>{order.client.name}</div>
                    <div>{order.client.phone}</div>
                </div>
                <div style={{width: '65%', ...cellStyle}}>
                    <table style={{borderSpacing: 0, width: '100%'}}>
                        {items}
                        {gifts}
                    </table>
                    <div style={{textAlign: 'right'}}>
                        <div>
                            <span style={bolderStyle}>{order.paymentTypeName}: </span>
                            <span style={boldStyle}>{order.paymentSum} р.</span>
                        </div>
                        {order.walletPayment > 0 && <div>Оплата баллами: {order.walletPayment} р.</div>}
                    </div>
                </div>
            </div>
            <div>{
                order.deliveryType == OrderStore.DELIVERY_TYPE.DELIVERY ?
                    order.address :
                    order.deliveryTypeName
            }</div>
            {this._renderExtraData()}
            {order.comment && <div>
                Комментарий клиента: <span style={bolderStyle}>{order.comment}</span>
            </div>}
        </div>;
    }
});
export default OrderInfo;
