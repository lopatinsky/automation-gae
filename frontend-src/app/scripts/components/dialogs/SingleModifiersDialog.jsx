import React from 'react';
import { Dialog, FlatButton, Divider } from 'material-ui';
import SingleModifier from './SingleModifier';

const SingleModifiersDialog = React.createClass({
    _getModifiers() {
        var modifiers = this.props.modifiers;
        const result = [];
        for (let modifier of modifiers) {
            result.push(
                <SingleModifier key={modifier.modifier_id}
                                modifier={modifier}
                                quantity={this.props.quantities[modifier.modifier_id]}
                                onChange={this.props.onChange}/>
            );
            result.push(<Divider key={`divider_${modifier.modifier_id}`}/>)
        }
        result.pop();
        return result;
    },

    render() {
        const actions = <FlatButton label='ОК' secondary={true} onTouchTap={this.props.requestClose}/>;
        return (
            <Dialog autoScrollBodyContent={true}
                    contentStyle={{width: '90%'}}
                    ref="modifierDialog"
                    title='Добавки'
                    open={this.props.open}
                    actions={actions}>
                {this._getModifiers()}
            </Dialog>
        );
    }
});

export default SingleModifiersDialog;