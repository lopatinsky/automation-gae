import React from 'react';
import mui from 'material-ui';
import { NavigationDrawer } from '../components';
import { LoadingDialog } from '../components/dialogs'
import theme from '../theme';
import { AppActions } from '../actions';
import { MenuStore } from '../stores';

const AppView = React.createClass({
    childContextTypes: {
        location: React.PropTypes.object,
        muiTheme: React.PropTypes.object
    },

    getChildContext() {
        return {
            location: this.props.location,
            muiTheme: theme
        };
    },

    refresh() {
        if (MenuStore.rootCategories.length == 0) {
            this.refs.processingDialog.show();
        } else {
            this.refs.processingDialog.dismiss();
        }
    },

    componentDidMount() {
        MenuStore.addChangeListener(this.refresh);
        AppActions.load();
        this.refresh();
    },

    componentWillUnmount() {
        MenuStore.removeChangeListener(this.refresh);
    },

    getDrawer() {
        return this.refs.drawer;
    },

    render() {
        let children = React.cloneElement(this.props.children, {getDrawer: this.getDrawer});
        return <div>
            <NavigationDrawer ref="drawer"/>
            {children}
            <LoadingDialog
                ref='processingDialog'
                title='Загрузка'/>
        </div>;
    }
});
export default AppView;