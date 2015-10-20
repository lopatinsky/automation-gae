import React from 'react';
import { Toolbar } from '../components';
import { AddressScreen } from '../components/screens'
import { Navigation } from 'react-router';

const AddressView = React.createClass({
    mixins: [Navigation],

    toolbarLeftTap() {
        this.refs.addressScreen.saveAddress();
        this.transitionTo('order');
    },

    render() {
        return (
            <div>
                <Toolbar title="Адрес" view={this} back={true} />
                <AddressScreen ref="addressScreen"/>
            </div>
        );
    }
});
export default AddressView;