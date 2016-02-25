import React from 'react';
import { Toolbar } from '../components';
import { SettingsScreen } from '../components/screens';

const SettingsView = React.createClass({
    toolbarLeftTap() {
        this.props.getDrawer().toggle();
    },
    render() {
        return (
            <div>
                <Toolbar title='Настройки' view={this} />
                <SettingsScreen />
            </div>
        );
    }
});
export default SettingsView;