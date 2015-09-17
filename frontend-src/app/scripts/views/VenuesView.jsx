import React from 'react';
import { Toolbar, VenuesScreen, NavigationDrawer } from '../components';

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