import React from 'react';
import { Dialog, TextField, FlatButton } from 'material-ui';
import { ClientStore } from '../stores';
import Actions from '../Actions';

const ClientInfoDialog = React.createClass({
    _refresh() {
        this.setState({});
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

    componentDidMount() {
        ClientStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        ClientStore.removeChangeListener(this._refresh);
    },

    render() {
        return (
            <Dialog ref="clientInfoDialog">
                <TextField hintText="Имя" ref="name" value={ClientStore.getName()} onChange={this._setClientInfo}/>
                <TextField hintText="Номер телефона" ref="phone" value={ClientStore.getPhone()} onChange={this._setClientInfo}/>
                <TextField hintText="Email" ref="email" value={ClientStore.getEmail()} onChange={this._setClientInfo}/>
                <FlatButton label="Ок" onClick={this._submit} />
            </Dialog>
        );
    }
});

export default ClientInfoDialog;