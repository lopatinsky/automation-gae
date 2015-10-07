import React from 'react';
import { RouteHandler } from 'react-router';
import mui from 'material-ui';
import theme from '../theme';

const AppView = React.createClass({

    childContextTypes: {
        muiTheme: React.PropTypes.object
    },

    getChildContext() {
        return {
            muiTheme: theme
        };
    },

    render() {
        return <RouteHandler/>;
    }
});
export default AppView;