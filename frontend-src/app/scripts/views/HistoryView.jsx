import React from 'react';
import { Toolbar, NavigationDrawer } from '../components';
import { HistoryScreen } from '../components/screens';

const HistoryView = React.createClass({
    toolbarLeftTap() {
        this.refs.navigationDrawer.toggle();
    },
    render() {
        return (
            <div>
                <Toolbar title='История' view={this} />
                <HistoryScreen />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default HistoryView;