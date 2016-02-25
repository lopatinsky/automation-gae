import React from 'react';
import { Toolbar } from '../components';
import { VenuesScreen } from '../components/screens';

const VenuesView = React.createClass({
    toolbarLeftTap() {
        this.props.getDrawer().toggle();
    },

    render() {
        return (
            <div>
                <Toolbar title='Кофейни' view={this} />
                <VenuesScreen />
            </div>
        );
    }
});
export default VenuesView;