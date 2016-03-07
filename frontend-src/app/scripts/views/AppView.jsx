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

    getInitialState() {
        return {
            loading: MenuStore.rootCategories.length == 0
        };
    },

    _onMenuStoreChanged() {
        this.setState({
            loading: MenuStore.rootCategories.length == 0
        });
    },

    componentDidMount() {
        MenuStore.addChangeListener(this._onMenuStoreChanged);
        AppActions.load();
    },

    componentWillUnmount() {
        MenuStore.removeChangeListener(this._onMenuStoreChanged);
    },

    getDrawer() {
        return this.refs.drawer;
    },

    render() {
        let children = React.cloneElement(this.props.children, {getDrawer: this.getDrawer});
        return <div>
            <NavigationDrawer ref="drawer"/>
            {children}
            <LoadingDialog ref='processingDialog'
                           title='Загрузка'
                           open={this.state.loading}/>
        </div>;
    }
});
export default AppView;