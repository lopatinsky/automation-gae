import React from 'react';
import { Toolbar } from '../components';
import { PromosScreen } from '../components/screens';

const PromosView = React.createClass({
    toolbarLeftTap() {
        this.props.getDrawer().toggle();
    },
    render() {
        return (
            <div>
                <Toolbar title='Акции' view={this} />
                <PromosScreen />
            </div>
        );
    }
});
export default PromosView;