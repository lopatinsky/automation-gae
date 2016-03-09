import React from 'react';
import Card from 'material-ui/lib/card/card';
import FontIcon from 'material-ui/lib/font-icon';
import TextField from 'material-ui/lib/text-field';
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
        AppActions.setClientInfo(this.state.name, this.state.phone, this.state.email);
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
            <Card style={{margin: '0 12px', padding: '0 9px'}}>
                <div style={{display: 'flex', alignItems: 'baseline'}}>
                    <FontIcon style={{flexBasis: 36}}
                              color={settings.primaryColor}
                              className="material-icons">
                        face
                    </FontIcon>
                    <TextField style={{flexGrow: 1}}
                               hintText="Иван Иванов"
                               floatingLabelText="Имя"
                               ref="name"
                               value={this.state.name}
                               onChange={this._refresh}/>
                </div>
                <div style={{display: 'flex', alignItems: 'baseline'}}>
                    <FontIcon style={{flexBasis: 36}}
                              color={settings.primaryColor}
                              className="material-icons">
                        stay_primary_portrait
                    </FontIcon>
                    <TextField style={{flexGrow: 1}}
                               hintText="+7 999 111-22-33"
                               floatingLabelText="Номер телефона"
                               ref="phone"
                               value={this.state.phone}
                               onChange={this._refresh}/>
                </div>
                <div style={{display: 'flex', alignItems: 'baseline'}}>
                    <FontIcon style={{flexBasis: 36}}
                              color={settings.primaryColor}
                              className="material-icons">
                        mail
                    </FontIcon>
                    <TextField style={{flexGrow: 1}}
                               hintText="name@example.com"
                               floatingLabelText="Email"
                               ref="email"
                               value={this.state.email}
                               onChange={this._refresh}/>
                </div>
            </Card>
        </div>;
    }
});

export default ProfileScreen;