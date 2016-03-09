import React from 'react';
import { Toolbar } from '../components';
import { HistoryScreen } from '../components/screens';

const HistoryView = React.createClass({
    toolbarLeftTap() {
        this.props.getDrawer().toggle();
    },
    render() {
        return (
            <div>
                <Toolbar title='История' view={this} />
                <HistoryScreen />
            </div>
        );
    }
});
export default HistoryView;