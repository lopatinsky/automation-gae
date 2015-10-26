import React from 'react';
import { CardMedia, ListDivider } from 'material-ui';


const HistoryOrderItem = React.createClass({

    _getGroupModifiers(item) {
        return item.group_modifiers.map(modifier => {
            return <div>
                {modifier.name}
            </div>;
        });
    },

    _getSingleModifiers(item) {
        return item.single_modifiers.map(modifier => {
            if (modifier.quantity > 0) {
                return <div>
                    {modifier.name + ' x ' + modifier.quantity}
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
            picCard = <div style={{display: 'table-cell', width: '20%', padding: '2px 0'}}>
                <CardMedia>
                    <img src={item.pic}/>
                </CardMedia>
            </div>;
        } else {
            width = '85%';
            picCard = <div/>;
        }
        return (
            <div>
                <div style={{width: '100%', display: 'table'}}>
                    {picCard}
                    <div style={{display: 'table-cell', padding: '12px', width: width, verticalAlign: 'middle'}}>
                        <div style={{lineHeight: '120%'}}>
                            <b>{item.title}</b>
                        </div>
                        <div style={{lineHeight: '120%'}}>
                            {this._getGroupModifiers(item)}
                            {this._getSingleModifiers(item)}
                        </div>
                    </div>
                    <div style={{display: 'table-cell', width: '15%', verticalAlign: 'middle', textAlign: 'right', paddingRight: '12px'}}>
                        <b>{'x' + item.quantity}</b>
                    </div>
                </div>
                <ListDivider/>
            </div>
        );
    }
});

export default HistoryOrderItem;