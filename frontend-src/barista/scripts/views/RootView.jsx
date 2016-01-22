import React from 'react';
import Actions from '../Actions';
import theme from '../theme';


const RootView = React.createClass({
    childContextTypes: {
        muiTheme: React.PropTypes.object
    },

    componentDidMount() {
        Actions.initApp();
    },

    getChildContext() {
        return {
            muiTheme: theme
        };
    },

    render() {
        return this.props.children;
    }
});
export default RootView;
