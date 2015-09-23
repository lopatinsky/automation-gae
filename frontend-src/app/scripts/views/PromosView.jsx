import React from 'react';
import { Toolbar, NavigationDrawer, PromosScreen } from '../components';

const PromosView = React.createClass({
    toolbarLeftTap() {
        this.refs.navigationDrawer.toggle();
    },
    render() {
        return (
            <div>
                <Toolbar title='Акции' view={this} />
                <PromosScreen />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default PromosView;