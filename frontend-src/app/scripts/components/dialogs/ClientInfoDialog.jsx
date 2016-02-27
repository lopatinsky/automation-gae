import React from 'react';
import { Dialog, TextField, FlatButton, Card } from 'material-ui';
import { ClientStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { AppActions } from '../../actions';

const ClientInfoDialog = React.createClass({
    _refresh() {
        this.setState({
            name: this.refs.name.getValue(),
            phone: this.refs.phone.getValue(),
            email: this.refs.email.getValue()
        });
    },

    _setClientInfo() {
        AppActions.setClientInfo(this.refs.name.getValue(), this.refs.phone.getValue(), this.refs.email.getValue());
    },

    _submit() {
        this._setClientInfo();
        ServerRequests.sendClientInfo();
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
                <Card style={{margin: '0 0 12px 0'}}>
                    <TextField
                        style={{margin: '0 0 0 12px', width: '95%'}}
                        hintText="Имя"
                        floatingLabelText="Имя"
                        ref="name"
                        value={this.state.name}
                        onChange={this._refresh}/>
                </Card>
                <Card style={{margin: '0 0 12px 0'}}>
                    <TextField
                        style={{margin: '0 0 0 12px', width: '95%'}}
                        hintText="Номер телефона"
                        floatingLabelText="Номер телефона"
                        ref="phone"
                        value={this.state.phone}
                        onChange={this._refresh}/>
                </Card>
                <Card style={{margin: '0 0 12px 0'}}>
                    <TextField
                        style={{margin: '0 0 0 12px', width: '95%'}}
                        hintText="Email"
                        floatingLabelText="Email"
                        ref="email"
                        value={this.state.email}
                        onChange={this._refresh}/>
                </Card>
                <div>
                    <FlatButton label="Ок" onTouchTap={this._submit} />
                </div>
            </Dialog>
        );
    }
});

export default ClientInfoDialog;