import React from 'react';
import { ClientStore, CompanyStore } from '../../stores';
import { List, ListItem, Divider, FontIcon } from 'material-ui';
import settings from '../../settings';

const SettingsScreen = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _onClientInfoTap() {
        this.context.router.push('/profile');
    },

    _onFeedback() {
        var mailto = `mailto:${'team@ru-beacon.ru'}?subject=Мобильное веб-приложение ${CompanyStore.getName()}&cc=${CompanyStore.getEmails()}`;
        window.open(mailto);
    },

    _getClientInfo() {
        return <ListItem
                primaryText={ClientStore.getRenderedInfo()}
                leftIcon={<FontIcon color={settings.primaryColor}
                                    className="material-icons">
                              perm_identity
                          </FontIcon>}
                onTouchTap={this._onClientInfoTap}/>;
    },

    _getFeedback() {
        return <ListItem
                primaryText='Написать нам'
                leftIcon={<FontIcon color={settings.primaryColor}
                                    className="material-icons">
                              feedback
                          </FontIcon>}
                onTouchTap={this._onFeedback}/>;
    },

    render() {
        return <div style={{padding: '64px 0 0 0'}}>
            <div style={{padding: '12px 0', textAlign: 'center'}}>
                <b>Ваш ID: {ClientStore.getClientId()}</b>
            </div>
            <List style={{paddingBottom: '0', paddingTop: '0'}}>
                <Divider/>
                {this._getClientInfo()}
                <Divider/>
                {this._getFeedback()}
                <Divider/>
            </List>
        </div>;
    }
});

export default SettingsScreen;