import React from 'react';
import { RouteHandler } from 'react-router';
import mui from 'material-ui';
import { Dialog, RefreshIndicator } from 'material-ui';
import theme from '../theme';
import { AppActions } from '../actions';
import { MenuStore } from '../stores';

const AppView = React.createClass({
    dialogTitle: "Загрузка...",

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
            <Dialog ref="processingDialog"
                    bodyStyle={{padding: '12px'}}>
                <div style={{display: 'table', width: '100%'}}>
                    <div style={{display: 'table-cell', height: '40', width: '40', verticalAlign: 'middle'}}>
                        <RefreshIndicator left={12} top={12} size={40} status="loading" />
                    </div>
                    <div style={{display: 'table-cell', paddingLeft: '12px', verticalAlign: 'middle'}}>
                        <b>{this.dialogTitle}</b>
                    </div>
                </div>
            </Dialog>
        </div>;
    }
});
export default AppView;