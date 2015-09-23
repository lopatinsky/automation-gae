import React from 'react';
import { Toolbar, NavigationDrawer, SettingsScreen } from '../components';

const SettingsView = React.createClass({
    toolbarLeftTap() {
        this.refs.navigationDrawer.toggle();
    },
    render() {
        return (
            <div>
                <Toolbar title='Настройки' view={this} />
                <SettingsScreen />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default SettingsView;