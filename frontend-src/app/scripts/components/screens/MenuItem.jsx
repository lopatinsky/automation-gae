import React from 'react';
import { Card, CardText, FlatButton, CardMedia } from 'material-ui';
import { OrderStore } from '../../stores';
import { Navigation } from 'react-router';
import { AppActions } from '../../actions';

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

    render() {
        var item = this.props.item;
        var picCard = <div style={{display: 'table-cell', width: '50%'}}>
            <CardMedia>
                <img src={item.pic}/>
            </CardMedia>
        </div>;
        if (item.pic == null || item.pic == '') {
            picCard = <div/>;
        }
        var descriptionCard = <div style={{height: '64px', overflow: 'hidden'}}>
            {item.description}
        </div>;
        if (item.description == '') {
            descriptionCard = <div/>;
        }
        return (
            <div style={{width: '100%', display: 'table'}}>
                <Card
                    style={{margin:'0 12px 12px'}}
                    onClick={this._onMenuItemTap}>
                    {picCard}
                    <div style={{display: 'table-cell', padding: '12px 0 0 12px'}}>
                        <div>
                            <b>{item.title}</b>
                        </div>
                        {descriptionCard}
                        <FlatButton
                            style={{align: 'right bottom', margin: '12px'}}
                            label={item.price}
                            onClick={this._addItem} />
                    </div>
                </Card>
            </div>
        );
    }
});

export default MenuItem;