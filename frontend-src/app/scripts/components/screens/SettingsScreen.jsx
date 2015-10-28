import React from 'react';
import { Navigation } from 'react-router';
import { ClientStore, CompanyStore } from '../../stores';
import { List, ListItem, ListDivider, FontIcon } from 'material-ui';
import settings from '../../settings';

const SettingsScreen = React.createClass({
    mixins: [Navigation],

    _onClientInfoTap() {
        this.transitionTo('profile', {
            settings: true
        });
    },

    _onFeedback() {
        var mailto = `mailto:${'team@ru-beacon.ru'}?subject=Мобильное веб-приложение ${CompanyStore.getName()}&cc=${CompanyStore.getEmails()}`;
        window.open(mailto);
    },

    _getClientInfo() {
        return <ListItem
                primaryText={ClientStore.getRenderedInfo()}
                leftIcon={<FontIcon style={{display: 'table-cell', verticalAlign: 'middle', fontSize: '18px'}}
                                    color={settings.primaryColor}
                                    className="material-icons">
                              perm_identity
                          </FontIcon>}
                onClick={this._onClientInfoTap}/>;
    },

    _getFeedback() {
        return <ListItem
                primaryText='Написать нам'
                leftIcon={<FontIcon style={{display: 'table-cell', verticalAlign: 'middle', fontSize: '18px'}}
                                    color={settings.primaryColor}
                                    className="material-icons">
                              feedback
                          </FontIcon>}
                onClick={this._onFeedback}/>;
    },

    render() {
        return <div style={{padding: '64px 0 0 0'}}>
            <div style={{padding: '12px', width: '100%', textAlign: 'center'}}>
                <b>{'Ваш ID: ' + ClientStore.getClientId()}</b> 
            </div>
            <List style={{paddingBottom: '0', paddingTop: '0'}}>
                <ListDivider/>
                {this._getClientInfo()}
                <ListDivider/>
                {this._getFeedback()}
                <ListDivider/>
            </List>
        </div>;
    }
});

export default SettingsScreen;