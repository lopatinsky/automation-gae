import React from 'react';
import { AppBar } from 'material-ui';

const Toolbar = React.createClass({

    leftTap() {
        if (this.props.view) {
            this.props.view.toolbarLeftTap();
        }
    },

    render() {
        return (
            <AppBar
                title={this.props.title}
                iconClassNameRight="muidocs-icon-navigation-expand-more"
                onLeftIconButtonTouchTap={this.leftTap} />
        );
    }
});

export default Toolbar;