import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { MenuItemStore } from '../stores';

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
            <Card>
                <FlatButton label="-" onClick={() => this._deduct()} />
                <CardText>
                    {modifier.title}:{this.quantity}
                </CardText>
                <FlatButton label="+" onClick={() => this._add()} />
            </Card>
        );
    }
});

export default SingleModifier;