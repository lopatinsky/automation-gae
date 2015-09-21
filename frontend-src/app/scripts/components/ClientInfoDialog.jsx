import React from 'react';
import { Dialog, TextField, FlatButton } from 'material-ui';
import { ClientStore } from '../stores';
import Actions from '../Actions';

const ClientInfoDialog = React.createClass({
    _setClientInfo() {
        ClientStore.setInfo(this.refs.name.getValue(), this.refs.phone.getValue(), this.refs.email.getValue());
        Actions.sendClientInfo();
        this.dismiss();
    },

    show() {
        this.refs.clientInfoDialog.show();
    },

    dismiss() {
         this.refs.clientInfoDialog.dismiss();
    },

    render() {
        return (
            <Dialog ref="clientInfoDialog">
                <TextField hintText="Имя" ref="name" value={ClientStore.getName()}/>
                <TextField hintText="Номер телефона" ref="phone" value={ClientStore.getPhone()}/>
                <TextField hintText="Email" ref="email" value={ClientStore.getEmail()}/>
                <FlatButton label="Ок" onClick={this._setClientInfo} />
            </Dialog>
        );
    }
});

export default ClientInfoDialog;