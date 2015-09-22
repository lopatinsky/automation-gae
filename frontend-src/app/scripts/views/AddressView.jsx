import React from 'react';
import { Toolbar, AddressScreen } from '../components';
import { Navigation } from 'react-router';

const AddressView = React.createClass({
    mixins: [Navigation],

    toolbarLeftTap() {
        this.transitionTo('order');
    },

    render() {
        return (
            <div>
                <Toolbar title="Адрес" view={this} back={true} />
                <AddressScreen/>
            </div>
        );
    }
});
export default AddressView;