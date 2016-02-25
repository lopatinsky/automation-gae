import React from 'react';
import { Card, CardText, FlatButton, Divider } from 'material-ui';
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
            <div>
                <div style={{display: 'table', width: '100%', padding: '3px 0'}}>
                     <div style={{display: 'table-cell', width: '15%', verticalAlign: 'middle'}}>
                        <b>{modifier.price  + 'p.'}</b>
                    </div>
                    <div style={{display: 'table-cell', padding: '0 0 0 12px', verticalAlign: 'middle'}}>
                        <div style={{lineHeight: '120%'}}>
                            {modifier.title}
                        </div>
                    </div>
                    <div style={{display: 'table-cell'}}>
                        <div style={{display: 'table', float: 'right', verticalAlign: 'middle'}}>
                            {this.quantity > 0 ?
                                <div style={{display: 'table-cell'}}>
                                    <FlatButton
                                        style={{width: '40px', minWidth: null}}
                                        label="-"
                                        onClick={() => this._deduct()} />
                                </div>
                            : null}
                            {this.quantity > 0 ?
                                <div style={{display: 'table-cell'}}>
                                    {this.quantity}
                                </div>
                            : null}
                            <div style={{display: 'table-cell'}}>
                                <FlatButton
                                    style={{width: '40px', minWidth: null}}
                                    label="+"
                                    onClick={() => this._add()} />
                            </div>
                        </div>
                    </div>
                </div>
                <Divider/>
            </div>
        );
    }
});

export default SingleModifier;