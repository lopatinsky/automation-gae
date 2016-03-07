import React from 'react';
import { ClientStore, CompanyStore } from '../../stores';
import Divider from 'material-ui/lib/divider';
import FontIcon from 'material-ui/lib/font-icon';
import List from 'material-ui/lib/lists/list';
import ListItem from 'material-ui/lib/lists/list-item';
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

    _onFullSiteTap() {
        window.open(CompanyStore.getSite());
    },

    _getClientInfo() {
        return <ListItem primaryText='Ваш профиль'
                         leftIcon={<FontIcon color={settings.primaryColor}
                                             className="material-icons">
                                       perm_identity
                                   </FontIcon>}
                         onTouchTap={this._onClientInfoTap}/>;
    },

    _getFeedback() {
        return <ListItem primaryText='Написать нам'
                         leftIcon={<FontIcon color={settings.primaryColor}
                                             className="material-icons">
                                       feedback
                                   </FontIcon>}
                         onTouchTap={this._onFeedback}/>;
    },

    _getFullSite() {
        const site = CompanyStore.getSite();
        if (site) {
            return <ListItem primaryText='Полная версия сайта'
                             leftIcon={<FontIcon color={settings.primaryColor}
                                                 className="material-icons">
                                           open_in_new
                                       </FontIcon>}
                             onTouchTap={this._onFullSiteTap}/>;
        }
        return null;
    },

    render() {
        let site = this._getFullSite();
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
                {site}
                {site && <Divider/>}
            </List>
        </div>;
    }
});

export default SettingsScreen;