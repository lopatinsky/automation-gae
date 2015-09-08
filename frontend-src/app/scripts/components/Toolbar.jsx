import React from 'react';
import { AppBar } from 'material-ui';

const Toolbar = React.createClass({
    render() {
        return (
            <AppBar
                title={this.props.title}
                iconClassNameRight="muidocs-icon-navigation-expand-more" />
        );
    }
});

export default Toolbar;