import React from 'react';
import { Toolbar, NavigationDrawer, HistoryScreen } from '../components';

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