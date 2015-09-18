import React from 'react';
import { RouteHandler, Navigation } from 'react-router';
import { OnResize } from 'react-window-mixins';
import { AppBar, Dialog, FlatButton, TextField } from 'material-ui';
import { Nav, SpinnerWrap } from '../components';
import { AuthStore, AjaxStore, OrderStore } from '../stores';
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

    _updateInterval: null,

    componentDidMount() {
        AuthStore.addChangeListener(this._onAuthStoreChange);
        AjaxStore.addChangeListener(this._onAjaxStoreChange);
        OrderStore.addChangeListener(this._onOrderStoreChange);
        Actions.loadCurrent();
        this._updateInterval = setInterval(() => Actions.loadUpdates(), 15000);
    },
    componentWillUnmount() {
        AuthStore.removeChangeListener(this._onAuthStoreChange);
        AjaxStore.removeChangeListener(this._onAjaxStoreChange);
        OrderStore.removeChangeListener(this._onOrderStoreChange);
        clearInterval(this._updateInterval);
    },

    getInitialState() {
        return {
            orderAhead: OrderStore.getOrderAheadOrders(),
            delivery: OrderStore.getDeliveryOrders(),
            loggingOut: AjaxStore.sending.logout
        };
    },
    _onAjaxStoreChange(data) {
        this.setState({ loggingOut: AjaxStore.sending.logout });
    },
    _onAuthStoreChange() {
        if (!AuthStore.token) {
            this.transitionTo("login");
        }
    },
    _onOrderStoreChange() {
        this.setState({
            orderAhead: OrderStore.getOrderAheadOrders(),
            delivery: OrderStore.getDeliveryOrders()
        });
    },

    _logoutSubmit() {
        Actions.logout(this.refs.logoutPassword.getValue());
    },

    _renderLogoutDialog() {
        let controlsProps = this.state.loggingOut ? { disabled: true } : {};
        let actions = [
            <FlatButton key='cancel'
                        label='Отмена'
                        onTouchTap={() => { this.refs.logoutDialog.dismiss() }}
                        {...controlsProps}/>,
            <FlatButton key='logout'
                        label='Выйти'
                        onTouchTap={this._logoutSubmit}
                        {...controlsProps}
                        secondary={true}/>
        ], contentStyle = { maxWidth: 400 };
        return <Dialog ref='logoutDialog'
                       title='Выход'
                       actions={actions}
                       contentStyle={contentStyle}>
            <SpinnerWrap show={this.state.loggingOut}>
                <TextField ref='logoutPassword'
                           type='password'
                           floatingLabelText='Пароль'
                           fullWidth={true}
                           {...controlsProps}
                           disabled={this.state.loggingOut}
                           onEnterKeyDown={this._logoutSubmit}/>
            </SpinnerWrap>
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
            <Nav horizontal={isHorizontal}
                 orderCount={this.state.orderAhead.length}
                 deliveryCount={this.state.delivery.length}/>
            <div style={contentStyle}>
                <RouteHandler orderAhead={this.state.orderAhead}
                              delivery={this.state.delivery}
                              onTouchTapCancel={this._onTouchTapCancel}
                              onTouchTapConfirm={this._onTouchTapConfirm}
                              onTouchTapDone={this._onTouchTapDone}
                              onTouchTapPostpone={this._onTouchTapPostpone}/>
            </div>
            {this._renderLogoutDialog()}
        </div>;
    },
    _onLogoutClick() {
        this.refs.logoutDialog.show();
    },
    _onTouchTapCancel(order) {
        Actions.cancelOrder(order);
    },
    _onTouchTapConfirm(order) {
        Actions.confirmOrder(order)
    },
    _onTouchTapDone(order) {
        Actions.doneOrder(order);
    },
    _onTouchTapPostpone(order) {
        Actions.postponeOrder(order, 5);
    }
});
export default MainView;
