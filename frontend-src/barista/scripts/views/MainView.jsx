import React from 'react';
import { RouteHandler, Navigation } from 'react-router';
import { OnResize } from 'react-window-mixins';
import { AppBar, Dialog, FlatButton, TextField, CircularProgress } from 'material-ui';
import { Nav } from '../components';
import { AuthStore, AjaxStore } from '../stores';
import Actions from '../Actions';

const MainView = React.createClass({
    mixins: [OnResize, Navigation],

    statics: {
        willTransitionTo(transition) {
            if (!AuthStore.token) {
                transition.redirect("login");
            }
        }
    },

    componentDidMount() {
        AuthStore.addChangeListener(this._onAuthStoreChange);
        AjaxStore.addChangeListener(this._onAjaxStoreChange);
    },
    componentWillUnmount() {
        AuthStore.removeChangeListener(this._onAuthStoreChange);
        AjaxStore.removeChangeListener(this._onAjaxStoreChange);
    },

    getInitialState() {
        return { loggingOut: AjaxStore.sending.logout };
    },
    _onAjaxStoreChange(data) {
        this.setState({ loggingOut: AjaxStore.sending.logout });
    },
    _onAuthStoreChange() {
        if (!AuthStore.token) {
            this.transitionTo("login");
        }
    },

    _logoutSubmit() {
        Actions.logout(this.refs.logoutPassword.getValue());
    },

    _renderLogoutDialog() {
        let controlsProps = this.state.loggingOut ? { style: { opacity: 0 }, disabled: true } : {};
        let actions = [
            <FlatButton label='Отмена'
                        onTouchTap={() => { this.refs.logoutDialog.dismiss() }}
                        {...controlsProps}/>,
            <FlatButton label='Выйти'
                        onTouchTap={this._logoutSubmit}
                        {...controlsProps}
                        secondary={true}/>
        ], contentStyle = { maxWidth: 400 }, progressStyles = {
            position: 'absolute',
            top: '50%',
            left: '50%',
            marginLeft: -25,
            marginTop: -25
        };
        return <Dialog ref='logoutDialog'
                       title='Выход'
                       actions={actions}
                       contentStyle={contentStyle}>
            <TextField ref='logoutPassword'
                       type='password'
                       floatingLabelText='Пароль'
                       fullWidth={true}
                       {...controlsProps}
                       onEnterKeyDown={this._logoutSubmit}/>
            {this.state.loggingOut && <CircularProgress style={progressStyles}/>}
        </Dialog>;
    },

    render() {
        let isHorizontal = this.state.window.width > this.state.window.height;
        let contentStyle = isHorizontal ? {paddingLeft: 100, paddingTop: 80} : {paddingTop: 180};
        return <div>
            <AppBar title={AuthStore.login}
                    showMenuIconButton={false}
                    iconElementRight={<FlatButton label='Выйти' onTouchTap={this._onLogoutClick}/>}
                    style={{position:'fixed',top:0}}/>
            <Nav horizontal={isHorizontal}/>
            <div style={contentStyle}>
                <RouteHandler/>
            </div>
            {this._renderLogoutDialog()}
        </div>;
    },
    _onLogoutClick() {
        this.refs.logoutDialog.show();
    }
});
export default MainView;
