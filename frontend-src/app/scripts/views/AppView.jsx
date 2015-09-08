import React from 'react';
import { RouteHandler } from 'react-router';
import mui from 'material-ui';
let Colors = mui.Styles.Colors;

const ThemeManager = new mui.Styles.ThemeManager();
ThemeManager.setPalette({
    primary1Color: Colors.lightGreen500,
    primary2Color: Colors.lightGreen700,
    primary3Color: Colors.lightGreen100,
    accent1Color: Colors.pinkA200,
    accent2Color: Colors.pinkA400,
    accent3Color: Colors.pinkA100
});

const AppView = React.createClass({

    childContextTypes: {
        muiTheme: React.PropTypes.object
    },

    getChildContext() {
        return {
            muiTheme: ThemeManager.getCurrentTheme()
        };
    },

    render() {
        return <RouteHandler/>;
    }
});
export default AppView;