import React from 'react';
import { Paper, RaisedButton, FontIcon } from 'material-ui';
import { OrderStore } from '../../stores';
import { AppActions } from '../../actions';
import Colors from 'material-ui/lib/styles/colors';

const MenuItem = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired,
    },

    _onMenuItemTap() {
        AppActions.setMenuItem(this.props.item);
        const category_id = this.props.category.info.category_id,
            item_id = this.props.item.id;
        this.context.router.push(`/item/${category_id}/${item_id}`);
    },

    _addItem(e) {
        e.stopPropagation();
        OrderStore.addItem(this.props.item);
    },

    _getButton() {
        var item = this.props.item;
        return <RaisedButton
            primary={true}
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
        const item = this.props.item;
        let picCard = null;
        if (item.pic) {
            const picCardStyle = {
                backgroundImage: `url(${item.pic})`,
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center',
                backgroundSize: 'contain',
                width: 140,
                flexShrink: 0
            };
            picCard = <div style={picCardStyle}/>;
        }
        const content = <div style={{padding: 12, flexGrow: 1}}>
            <div style={{marginBottom: 4}}>{item.title}</div>
            {item.description && <div style={{fontSize: 12, marginBottom: 4}}>{item.description}</div>}
            {item.weight > 0 && <div style={{fontSize: 12, marginBottom: 4}}>{item.weight} г</div>}
            {item.volume > 0 && <div style={{fontSize: 12, marginBottom: 4}}>{item.volume} мл</div>}
            <div style={{textAlign: 'right'}}>
                {this._getButton()}
            </div>
        </div>;
        return <Paper style={{margin:'0 12px 12px', display: 'flex'}}
                      onClick={this._onMenuItemTap}>
            {picCard}
            {content}
        </Paper>
    }
});

export default MenuItem;