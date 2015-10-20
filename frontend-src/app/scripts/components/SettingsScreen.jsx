import React from 'react';
import { ClientStore } from '../stores';

const SettingsScreen = React.createClass({
    render() {
        return <div style={{padding: '64px 0 0 0'}}>
            <div style={{height: '124px', width: '100%', textAlign: 'center'}}>
                <b>{'Ваш ID: ' + ClientStore.getClientId()}</b> 
            </div>
        </div>;
    }
});

export default SettingsScreen;