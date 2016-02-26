import React from 'react';
import { Card, CardText, FlatButton, Divider } from 'material-ui';

const SingleModifier = React.createClass({
    _add() {
        this.props.onChange(this.props.modifier.modifier_id, this.props.quantity + 1);
    },

    _deduct() {
        if (this.props.quantity > 0) {
            this.props.onChange(this.props.modifier.modifier_id, this.props.quantity - 1);
        }
    },

    render() {
        var modifier = this.props.modifier;
        return (
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
                        {this.props.quantity > 0 ?
                            <div style={{display: 'table-cell'}}>
                                <FlatButton
                                    style={{width: '40px', minWidth: null}}
                                    label="-"
                                    onClick={this._deduct} />
                            </div>
                        : null}
                        {this.props.quantity > 0 ?
                            <div style={{display: 'table-cell'}}>
                                {this.props.quantity}
                            </div>
                        : null}
                        <div style={{display: 'table-cell'}}>
                            <FlatButton
                                style={{width: '40px', minWidth: null}}
                                label="+"
                                onClick={this._add} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

export default SingleModifier;