import React from 'react';
import { Dialog, FlatButton } from 'material-ui';
import { MenuItemStore } from '../stores';
import { SingleModifier } from '../components';

const SingleModifiersDialog = React.createClass({
    _getModifiers() {
        var modifiers = this.state.modifiers;
        return modifiers.map(modifier => {
            return (
                <SingleModifier modifier={modifier} />
            );
        });
    },

    _refresh() {
        this.setState({
            modifiers: MenuItemStore.getSingleModifiers()
        });
    },

    getInitialState: function() {
        return {
            modifiers: []
        }
    },

    show() {
        this._refresh();
        this.refs.modifierDialog.show();
    },

    dismiss() {
         this.refs.modifierDialog.dismiss();
    },

    render() {
        return (
            <Dialog
                autoScrollBodyContent="true"
                ref="modifierDialog"
                title='Добавки'>
                {this._getModifiers()}
                <FlatButton label='Ок' onClick={this.dismiss} />
            </Dialog>
        );
    }
});

export default SingleModifiersDialog;