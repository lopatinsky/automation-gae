import React from 'react';
import { Dialog, FlatButton } from 'material-ui';
import { MenuItemStore } from '../../stores';
import SingleModifier from './SingleModifier';

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
                contentStyle={{width: '90%'}}
                ref="modifierDialog"
                title='Добавки'
                actions={[{text: 'Ок', onTouchTap: this.dismiss}]}>
                {this._getModifiers()}
            </Dialog>
        );
    }
});

export default SingleModifiersDialog;