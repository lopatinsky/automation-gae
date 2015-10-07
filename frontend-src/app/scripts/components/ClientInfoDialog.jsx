import React from 'react';
import { Dialog, TextField, FlatButton } from 'material-ui';
import { ClientStore } from '../stores';
import Actions from '../Actions';

const ClientInfoDialog = React.createClass({
    _refresh() {
        this.setState({
            name: this.refs.name.getValue(),
            phone: this.refs.phone.getValue(),
            email: this.refs.email.getValue()
        });
    },

    _setClientInfo() {
        Actions.setClientInfo(this.refs.name.getValue(), this.refs.phone.getValue(), this.refs.email.getValue());
    },

    _submit() {
        this._setClientInfo();
        Actions.sendClientInfo();
        this.dismiss();
    },

    show() {
        this.refs.clientInfoDialog.show();
    },

    dismiss() {
         this.refs.clientInfoDialog.dismiss();
    },

    getInitialState() {
        return {
            name: ClientStore.getName(),
            phone: ClientStore.getPhone(),
            email: ClientStore.getEmail()
        }
    },

    render() {
        return (
            <Dialog ref="clientInfoDialog">
                <TextField hintText="Имя" ref="name" value={this.state.name} onChange={this._refresh}/>
                <TextField hintText="Номер телефона" ref="phone" value={this.state.phone} onChange={this._refresh}/>
                <TextField hintText="Email" ref="email" value={this.state.email} onChange={this._refresh}/>
                <FlatButton label="Ок" onClick={this._submit} />
            </Dialog>
        );
    }
});

export default ClientInfoDialog;