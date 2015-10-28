import React from 'react';
import { Toolbar } from '../components';
import { ProfileScreen } from '../components/screens'
import { Navigation } from 'react-router';

const ProfileView = React.createClass({
    mixins: [Navigation],

    toolbarLeftTap() {
        this.refs.profileScreen.saveProfile();
        var settings = this.props.params.settings;
        if (settings) {
            this.transitionTo('settings');
        } else {
            this.transitionTo('order');
        }
    },

    render() {
        return (
            <div>
                <Toolbar title="Профиль" view={this} back={true} />
                <ProfileScreen ref="profileScreen"/>
            </div>
        );
    }
});
export default ProfileView;