import React from 'react';
import { Card, CardText, RaisedButton, CardMedia, FontIcon } from 'material-ui';
import { OrderStore } from '../../stores';
import { Navigation } from 'react-router';
import { AppActions } from '../../actions';
import Colors from 'material-ui/lib/styles/colors';

const MenuItem = React.createClass({
    mixins: [Navigation],

    _onMenuItemTap() {
        AppActions.setMenuItem(this.props.item);
        this.transitionTo('menu_item', {
            category_id: this.props.category.info.category_id,
            item_id: this.props.item.id
        });
    },

    _addItem(e) {
        e.stopPropagation();
        OrderStore.addItem(this.props.item);
    },

    _getButton(tableCell) {
        var item = this.props.item;
        var style = {position: 'absolute', right: 12, bottom: 12};
        return <RaisedButton
            primary={true}
            style={style}
            label={item.price}
            onClick={this._addItem}>
            <FontIcon style={{verticalAlign: 'middle', fontSize: '18px'}}
                      color={Colors.white}
                      className="material-icons">
                add_shopping_cart
            </FontIcon>
        </RaisedButton>;
    },

    render() {
        var item = this.props.item;
        var picCard = <div style={{display: 'table-cell', width: '50%'}}>
            <CardMedia>
                <img src={item.pic}/>
            </CardMedia>
        </div>;
        if (item.pic == null || item.pic == '') {
            picCard = '';
        }
        var descriptionCard = <div style={{maxHeight: '64px', overflow: 'hidden', lineHeight: '120%', padding: '6px 0 0 0'}}>
            {item.description}
        </div>;
        if (item.description == '') {
            descriptionCard = <div/>;
        }
        var grCard = <div/>;
        if (item.weight > 0) {
            grCard = <div style={{padding: '6px 0 0 0'}}>
                {item.weight + ' г'}
            </div>;
        }
        if (item.volume > 0) {
            grCard = <div style={{padding: '6px 0 0 0'}}>
                {item.volume + ' мл'}
            </div>;
        }
        return (
            <div style={{width: '100%', display: 'table'}}>
                <Card
                    style={{margin:'0 12px 12px', position: 'relative', minHeight: '64px'}}
                    onClick={this._onMenuItemTap}>
                    {picCard}
                    <div style={{display: 'table-cell', padding: '12px 12px 0 12px'}}>
                        <div style={{lineHeight: '120%'}}>
                            <b>{item.title}</b>
                        </div>
                        {descriptionCard}
                        {grCard}
                        {picCard != '' ? <div style={{height:60}}/> : ''}
                        {picCard != '' ? this._getButton(false) : ''}
                    </div>
                    {picCard == '' ? this._getButton(true) : ''}
                </Card>
            </div>
        );
    }
});

export default MenuItem;