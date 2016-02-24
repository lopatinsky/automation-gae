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
            open: false,
            modifiers: []
        }
    },

    show() {
        this._refresh();
        this.setState({
            open: true
        })
    },

    dismiss() {
        this.setState({
            open: false
        })
    },

    render() {
        return (
            <Dialog
                autoScrollBodyContent={true}
                contentStyle={{width: '90%'}}
                ref="modifierDialog"
                title='Добавки'
                open={this.state.open}
                actions={[{text: 'Ок', onTouchTap: this.dismiss}]}>
                {this._getModifiers()}
            </Dialog>
        );
    }
});

export default SingleModifiersDialog;