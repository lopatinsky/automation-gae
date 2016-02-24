import React from 'react';
import { Toolbar } from '../components';
import { ProfileScreen } from '../components/screens'

const ProfileView = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    toolbarLeftTap() {
        this.refs.profileScreen.saveProfile();
        this.router.goBack();
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