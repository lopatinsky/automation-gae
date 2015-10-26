import React from 'react';
import { RouteHandler } from 'react-router';
import mui from 'material-ui';
import { LoadingDialog } from '../components/dialogs'
import theme from '../theme';
import { AppActions } from '../actions';
import { MenuStore } from '../stores';

const AppView = React.createClass({
    childContextTypes: {
        muiTheme: React.PropTypes.object
    },

    getChildContext() {
        return {
            muiTheme: theme
        };
    },

    refresh() {
        if (MenuStore.getCategories().length == 0) {
            this.refs.processingDialog.show();
        } else {
            this.refs.processingDialog.dismiss();
        }
    },

    componentDidMount() {
        MenuStore.addChangeListener(this.refresh);
        if (MenuStore.getCategories().length == 0) {
            AppActions.load();
        }
        this.refresh();
    },

    componentWillUnmount() {
        MenuStore.removeChangeListener(this.refresh);
        this.refs.processingDialog.dismiss();
    },

    render() {
        return <div>
            <RouteHandler/>
            <LoadingDialog
                ref='processingDialog'
                title='Загрузка'/>
        </div>;
    }
});
export default AppView;