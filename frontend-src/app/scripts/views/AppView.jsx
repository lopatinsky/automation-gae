import React from 'react';
import mui from 'material-ui';
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
            {this.props.children}
            <LoadingDialog
                ref='processingDialog'
                title='Загрузка'/>
        </div>;
    }
});
export default AppView;