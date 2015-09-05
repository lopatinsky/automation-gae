import React from 'react';
import { Nav } from '../components';

const Toolbar = React.createClass({
    render() {
        return (
            <AppBar
                title="Title"
                iconClassNameRight="muidocs-icon-navigation-expand-more" />
        );
    }
});

export default Toolbar;