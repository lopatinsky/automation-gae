import React from 'react';
import { Toolbar, NavigationDrawer } from '../components';
import { SettingsScreen } from '../components/screens';

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