import React from 'react';
import { TextField, Card, FlatButton, FontIcon } from 'material-ui';
import { ClientStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { AppActions } from '../../actions';
import settings from '../../settings';

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
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '0 12px 12px 12px'}}>
                    <div style={{display: 'table-cell', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '18px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            face
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <TextField
                            style={{width: '100%'}}
                            hintText="Имя"
                            floatingLabelText="Имя"
                            ref="name"
                            value={this.state.name}
                            onChange={this._refresh}/>
                    </div>
                </Card>
            </div>
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '0 12px 12px 12px'}}>
                    <div style={{display: 'table-cell', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '18px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            stay_primary_portrait
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <TextField
                            style={{width: '100%'}}
                            hintText="Номер телефона"
                            floatingLabelText="Номер телефона"
                            ref="phone"
                            value={this.state.phone}
                            onChange={this._refresh}/>
                    </div>
                </Card>
            </div>
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '0 12px 12px 12px'}}>
                    <div style={{display: 'table-cell', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '18px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            mail
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <TextField
                            style={{width: '100%'}}
                            hintText="Email"
                            floatingLabelText="Email"
                            ref="email"
                            value={this.state.email}
                            onChange={this._refresh}/>
                    </div>
                </Card>
            </div>
        </div>;
    }
});

export default ProfileScreen;