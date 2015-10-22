import React from 'react';
import { TextField, Card, FlatButton } from 'material-ui';
import { ClientStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { AppActions } from '../../actions';

const ProfileScreen = React.createClass({
     _refresh() {
        this.setState({
            name: this.refs.name.getValue(),
            phone: this.refs.phone.getValue(),
            email: this.refs.email.getValue()
        });
    },

    saveProfile() {
        ServerRequests.sendClientInfo();
        AppActions.setClientInfo(this.refs.name.getValue(), this.refs.phone.getValue(), this.refs.email.getValue());
    },

    getInitialState() {
        return {
            name: ClientStore.getName(),
            phone: ClientStore.getPhone(),
            email: ClientStore.getEmail()
        }
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            <Card style={{margin: '0 12px 12px 12px'}}>
                <TextField
                    style={{margin: '0 0 0 12px', width: '95%'}}
                    hintText="Имя"
                    floatingLabelText="Имя"
                    ref="name"
                    value={this.state.name}
                    onChange={this._refresh}/>
            </Card>
            <Card style={{margin: '0 12px 12px 12px'}}>
                <TextField
                    style={{margin: '0 0 0 12px', width: '95%'}}
                    hintText="Номер телефона"
                    floatingLabelText="Номер телефона"
                    ref="phone"
                    value={this.state.phone}
                    onChange={this._refresh}/>
            </Card>
            <Card style={{margin: '0 12px 12px 12px'}}>
                <TextField
                    style={{margin: '0 0 0 12px', width: '95%'}}
                    hintText="Email"
                    floatingLabelText="Email"
                    ref="email"
                    value={this.state.email}
                    onChange={this._refresh}/>
            </Card>
        </div>;
    }
});

export default ProfileScreen;