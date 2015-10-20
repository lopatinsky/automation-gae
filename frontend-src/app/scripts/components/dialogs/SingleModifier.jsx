import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { MenuItemStore } from '../../stores';

const SingleModifier = React.createClass({
    quantity: 0,

    _refresh() {
        this.setState({
            quantity: this.quantity
        });
    },

    _add() {
        this.quantity += 1;
        this._refresh();
    },

    _deduct() {
        if (this.quantity > 0) {
            this.quantity -= 1;
        }
        this._refresh();
    },

    getInitialState() {
        var modifier = this.props.modifier;
        this.quantity = modifier.quantity;
        return {
            quantity: this.quantity
        }
    },

    componentWillUnmount() {
        var modifier = this.props.modifier;
        MenuItemStore.setSingleModifierNumber(modifier.modifier_id, this.quantity);
    },

    render() {
        var modifier = this.props.modifier;
        return (
            <Card style={{margin: '0 0 6px 0'}}>
                <div style={{display: 'table'}}>
                    {modifier.price != 0 ? <div style={{display: 'table-cell', width: '24px', padding: '0 0 0 3px'}}>
                        {modifier.price  + 'p. '}
                    </div> : ''}
                    <div style={{display: 'table-cell', width: '100px', padding: '0 0 0 12px'}}>
                        {modifier.title}
                    </div>
                    <div style={{display: 'table-cell', padding: '12px'}}>
                        <FlatButton
                            style={{width: '40px', minWidth: null}}
                            label="-"
                            onClick={() => this._deduct()} />
                    </div>
                    <div style={{display: 'table-cell', textAlign: 'center'}}>
                        {this.quantity}
                    </div>
                    <div style={{display: 'table-cell', padding: '12px'}}>
                        <FlatButton
                            style={{width: '40px', minWidth: null}}
                            label="+"
                            onClick={() => this._add()} />
                    </div>
                </div>
            </Card>
        );
    }
});

export default SingleModifier;