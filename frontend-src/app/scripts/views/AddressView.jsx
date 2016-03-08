import React from 'react';
import { Toolbar } from '../components';
import { AddressScreen } from '../components/screens'

const AddressView = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired,
    },

    toolbarLeftTap() {
        this.refs.addressScreen.saveAddress();
        this.context.router.goBack();
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