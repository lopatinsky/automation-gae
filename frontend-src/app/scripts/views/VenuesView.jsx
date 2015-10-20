import React from 'react';
import { Toolbar, NavigationDrawer } from '../components';
import { VenuesScreen } from '../components/screens';

const VenuesView = React.createClass({
    toolbarLeftTap() {
        this.refs.navigationDrawer.toggle();
    },

    render() {
        return (
            <div>
                <Toolbar title='Кофейни' view={this} />
                <VenuesScreen />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default VenuesView;