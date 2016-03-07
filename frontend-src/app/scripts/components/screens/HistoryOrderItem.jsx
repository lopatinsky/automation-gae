import React from 'react';
import { CardMedia, Divider } from 'material-ui';


const HistoryOrderItem = React.createClass({
    _getGroupModifiers(item) {
        return item.group_modifiers.map((modifier, i) => {
            return <div key={i}>
                {modifier.name}
            </div>;
        });
    },

    _getSingleModifiers(item) {
        return item.single_modifiers.map((modifier, i) => {
            if (modifier.quantity > 0) {
                return <div key={i}>
                    {modifier.name + ' x' + modifier.quantity}
                </div>;
            }
        });
    },

    render() {
        var item = this.props.item;
        var width;
        var picCard;
        if (item.pic != null && item.pic != '') {
            width = '65%';
            picCard = <div style={{display: 'table-cell', width: '20%', padding: '2px 0', verticalAlign: 'middle'}}>
                <CardMedia>
                    <img src={item.pic}/>
                </CardMedia>
            </div>;
        } else {
            width = '85%';
            picCard = null;
        }
        return (
            <div>
                <div style={{width: '100%', display: 'table'}}>
                    {picCard}
                    <div style={{display: 'table-cell', padding: '12px', width: width, verticalAlign: 'middle'}}>
                        <div style={{lineHeight: '120%'}}>
                            {item.title}
                        </div>
                        <div style={{fontSize: 12, lineHeight: '120%'}}>
                            {this._getGroupModifiers(item)}
                            {this._getSingleModifiers(item)}
                        </div>
                    </div>
                    <div style={{display: 'table-cell', width: '15%', verticalAlign: 'middle', textAlign: 'right', paddingRight: '12px'}}>
                        x{item.quantity}
                    </div>
                </div>
                <Divider/>
            </div>
        );
    }
});

export default HistoryOrderItem;