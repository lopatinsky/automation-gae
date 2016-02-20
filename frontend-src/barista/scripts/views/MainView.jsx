import React from 'react';
import { OnResize } from 'react-window-mixins';
import AppBar from 'material-ui/lib/app-bar';
import Checkbox from 'material-ui/lib/checkbox';
import Dialog from 'material-ui/lib/dialog';
import FlatButton from 'material-ui/lib/flat-button';
import IconButton from 'material-ui/lib/icon-button';
import IconMenu from 'material-ui/lib/menus/icon-menu';
import MenuItem from 'material-ui/lib/menus/menu-item';
import MoreVertIcon from 'material-ui/lib/svg-icons/navigation/more-vert';
import TextField from 'material-ui/lib/text-field';
import RadioButtonGroup from 'material-ui/lib/radio-button-group';
import RadioButton from 'material-ui/lib/radio-button';
import RaisedButton from 'material-ui/lib/raised-button';
import { Nav, SpinnerWrap, Clock } from '../components';
import { AuthStore, AjaxStore, OrderStore, SystemStore, ConfigStore } from '../stores';
import Actions from '../Actions';

const MainView = React.createClass({
    mixins: [OnResize],

    statics: {
        onEnter(nextState, replace) {
            if (!AuthStore.token) {
                replace('/login');
            }
        }
    },

    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _updateInterval: null,

    componentDidMount() {
        AuthStore.addChangeListener(this._onAuthStoreChange);
        AjaxStore.addChangeListener(this._onAjaxStoreChange);
        OrderStore.addChangeListener(this._onOrderStoreChange);
        SystemStore.addChangeListener(this._onSystemStoreChange);
        ConfigStore.addChangeListener(this._onConfigStoreChange);
        Actions.loadCurrent();
        Actions.loadConfig();
        this._checkDeliveryType();
    },
    componentWillUnmount() {
        AuthStore.removeChangeListener(this._onAuthStoreChange);
        AjaxStore.removeChangeListener(this._onAjaxStoreChange);
        OrderStore.removeChangeListener(this._onOrderStoreChange);
        SystemStore.removeChangeListener(this._onSystemStoreChange);
        ConfigStore.removeChangeListener(this._onConfigStoreChange);
        clearInterval(this._updateInterval);
    },

    getInitialState() {
        return {
            hasUpdate: SystemStore.hasUpdate,
            orderAheadEnabled: ConfigStore.orderAheadEnabled,
            deliveryEnabled: ConfigStore.deliveryEnabled,
            appKind: ConfigStore.appKind,
            orderAhead: OrderStore.getOrderAheadOrders(),
            delivery: OrderStore.getDeliveryOrders(),
            loadingOrders: AjaxStore.sending.current,
            loadedOrders: OrderStore.loadedOrders,
            lastSuccessfulLoadTime: OrderStore.lastSuccessfulLoadTime,
            wasLastLoadSuccessful: OrderStore.wasLastLoadSuccessful,
            pendingAction: null,
            pendingOrder: null,
            loggingOut: AjaxStore.sending.logout
        };
    },
    _onAjaxStoreChange(data) {
        this.setState({
            loadingOrders: AjaxStore.sending.current,
            loggingOut: AjaxStore.sending.logout
        });
    },
    _onAuthStoreChange() {
        if (!AuthStore.token) {
            this.context.router.push("/login");
        }
    },
    _onOrderStoreChange(data) {
        this.setState({
            orderAhead: OrderStore.getOrderAheadOrders(),
            delivery: OrderStore.getDeliveryOrders(),
            loadedOrders: OrderStore.loadedOrders,
            lastSuccessfulLoadTime: OrderStore.lastSuccessfulLoadTime,
            wasLastLoadSuccessful: OrderStore.wasLastLoadSuccessful
        });
        if (this._updateInterval == null && OrderStore.loadedOrders) {
            this._updateInterval = setInterval(() => Actions.loadUpdates(), 15000);
        }
        if (data && data.notify) {
            SystemStore.playSound();
        }
        this._checkDeliveryType();
    },
    _onSystemStoreChange() {
        this.setState({
            hasUpdate: SystemStore.hasUpdate
        });
    },
    _onConfigStoreChange() {
        this.setState({
            orderAheadEnabled: ConfigStore.orderAheadEnabled,
            deliveryEnabled: ConfigStore.deliveryEnabled,
            appKind: ConfigStore.appKind
        })
    },

    _checkDeliveryType() {
        if (!this.state.orderAheadEnabled && this.context.router.isActive("current")) {
            this.context.router.push("/delivery");
        } else if (!this.state.deliveryEnabled && this.context.router.isActive("delivery")) {
            this.context.router.push("/current");
        }
    },

    _logoutSubmit() {
        Actions.logout(this.refs.logoutPassword.getValue());
    },

    _renderAppBar() {
        let rightEl = <IconMenu iconButtonElement={<IconButton><MoreVertIcon/></IconButton>}
                                targetOrigin={{horizontal: 'right', vertical: 'top'}}
                                anchorOrigin={{horizontal: 'right', vertical: 'top'}}>
            <MenuItem primaryText='Настройки'
                      onTouchTap={this._onSettingsClick}/>
            <MenuItem primaryText='Выйти'
                      onTouchTap={this._onLogoutClick}/>
        </IconMenu>;
        return <AppBar title={AuthStore.login}
                       showMenuIconButton={false}
                       iconElementRight={rightEl}
                       style={{position:'fixed',top:0}}/>
    },

    _renderSettingsDialog() {
        let actions = [
            <FlatButton key='cancel'
                        label='Отмена'
                        onTouchTap={this._clearPendingAction}/>,
            <FlatButton key='save'
                        label='Сохранить'
                        onTouchTap={this._settingsSave}
                        secondary={true}/>
        ];
        return <Dialog ref='settingsDialog'
                       title='Настройки'
                       actions={actions}
                       open={this.state.pendingAction == 'settings'}>
            <Checkbox label="Повторное оповещение за 5 минут до заказа"
                      ref="additionalSoundNotification"
                      defaultChecked={ConfigStore.userSettings.additionalSoundNotification}/>
        </Dialog>;
    },

    _renderLogoutDialog() {
        let controlsProps = this.state.loggingOut ? { disabled: true } : {};
        let actions = [
            <FlatButton key='cancel'
                        label='Отмена'
                        onTouchTap={this._clearPendingAction}
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
                       contentStyle={contentStyle}
                       open={this.state.pendingAction == 'logout'}>
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

    _renderCancelDialog() {
        let actions = [
            <FlatButton key='back'
                        label='Назад'
                        onTouchTap={this._clearPendingAction}/>,
            <FlatButton key='ok'
                        label='Отменить заказ'
                        secondary={true}
                        onTouchTap={this._cancelSubmit}/>
        ];
        return <Dialog ref='cancelDialog'
                       title='Отмена заказа'
                       actions={actions}
                       contentStyle={{maxWidth: 600}}
                       open={this.state.pendingAction == 'cancel'}>
            <TextField ref='returnComment'
                       type='text'
                       floatingLabelText='Введите комментарий'
                       fullWidth={true}/>
        </Dialog>
    },

    _renderPostponeDialog() {
        let actions = [
            <FlatButton key='back'
                        label='Назад'
                        onTouchTap={this._clearPendingAction}/>,
            <FlatButton key='ok'
                        label='Перенести'
                        secondary={true}
                        onTouchTap={this._postponeSubmit}/>
        ],
            options = OrderStore.POSTPONE_OPTIONS.map(
                    i => <RadioButton key={i}
                                      value={'' + i}
                                      label={`${i} минут`}
                                      style={{marginBottom: 8}}/>
            );
        return <Dialog ref='postponeDialog'
                       title='Перенос заказа'
                       actions={actions}
                       contentStyle={{maxWidth: 400}}
                       open={this.state.pendingAction == 'postpone'}>
            <RadioButtonGroup name='postponeMinutes'
                              ref='postponeMinutes'
                              defaultSelected='10'>
                {options}
            </RadioButtonGroup>
        </Dialog>
    },

    _renderMoveDialog() {
        let actions = [
            <FlatButton key='back'
                        label='Назад'
                        onTouchTap={this._clearPendingAction}/>,
            <FlatButton key='ok'
                        label='Перенести'
                        secondary={true}
                        onTouchTap={this._moveSubmit}/>
        ], venues = ConfigStore.venues.filter(
            venue => venue.id != ConfigStore.thisVenue
        ).map(
            venue => <RadioButton key={venue.id}
                                  value={'' + venue.id}
                                  label={venue.title}
                                  style={{marginBottom: 8}}/>
        );
        return <Dialog ref='moveDialog'
                       title='Перенос на другую точку'
                       actions={actions}
                       contentStyle={{maxWidth: 600}}
                       open={this.state.pendingAction == 'move'}>
            <RadioButtonGroup name='moveVenue'
                              ref='moveVenue'
                              defaultSelected={venues[0] && venues[0].props.value}>
                {venues}
            </RadioButtonGroup>
        </Dialog>
    },

    render() {
        let isHorizontal = this.state.window.width > this.state.window.height;
        let contentStyle = isHorizontal ? {paddingLeft: 100, paddingTop: 116} : {paddingTop: 216};
        return <div>
            {this._renderAppBar()}
            <Nav horizontal={isHorizontal}
                 showCurrent={this.state.orderAheadEnabled}
                 orderCount={this.state.orderAhead.length}
                 showDelivery={this.state.deliveryEnabled}
                 deliveryCount={this.state.delivery.length}/>
            <Clock horizontal={isHorizontal} lastUpdate={this.state.lastSuccessfulLoadTime}>
                {this.state.hasUpdate &&
                    <RaisedButton label="Новая версия"
                                  secondary={true}
                                  style={{verticalAlign: 'middle'}}
                                  onTouchTap={() => window.location.reload()}/>
                }
            </Clock>
            <div style={contentStyle}>
                {React.cloneElement(this.props.children, {
                    loadedOrders: this.state.loadedOrders,
                    loadingOrders: this.state.loadingOrders,
                    orderAhead: this.state.orderAhead,
                    delivery: this.state.delivery,
                    appKind: this.state.appKind,
                    tryReload: this._tryReloadOrders,
                    onTouchTapCancel: this._onTouchTapCancel,
                    onTouchTapConfirm: this._onTouchTapConfirm,
                    onTouchTapDone: this._onTouchTapDone,
                    onTouchTapPostpone: this._onTouchTapPostpone,
                    onTouchTapMove: this._onTouchTapMove,
                    onTouchTapSync: this._onTouchTapSync
                })}
            </div>
            {this._renderSettingsDialog()}
            {this._renderLogoutDialog()}
            {this._renderCancelDialog()}
            {this._renderPostponeDialog()}
            {this._renderMoveDialog()}
        </div>;
    },
    _tryReloadOrders() {
        if (!this.state.loadedOrders && !this.state.loadingOrders) {
            Actions.loadCurrent();
        }
    },

    _clearPendingAction() {
        this.setState({
            pendingAction: null,
            pendingOrder: null
        })
    },

    _onSettingsClick() {
        this.setState({ pendingAction: 'settings' })
    },

    _settingsSave() {
        Actions.saveUserSettings({
            additionalSoundNotification: this.refs.additionalSoundNotification.isChecked()
        });
        this._clearPendingAction();
    },

    _onLogoutClick() {
        this.setState({ pendingAction: 'logout' })
    },

    _onTouchTapCancel(order) {
        this.setState({
            pendingAction: 'cancel',
            pendingOrder: order
        });
    },
    _cancelSubmit() {
        Actions.cancelOrder(this.state.pendingOrder, this.refs.returnComment.getValue());
        this._clearPendingAction();
    },

    _onTouchTapConfirm(order) {
        Actions.confirmOrder(order)
    },
    _onTouchTapDone(order) {
        Actions.doneOrder(order);
    },

    _onTouchTapPostpone(order) {
        this.setState({
            pendingAction: 'postpone',
            pendingOrder: order
        });
    },
    _postponeSubmit() {
        Actions.postponeOrder(this.state.pendingOrder, this.refs.postponeMinutes.getSelectedValue());
        this._clearPendingAction();
    },

    _onTouchTapMove(order) {
        this.setState({
            pendingAction: 'move',
            pendingOrder: order
        });
    },
    _moveSubmit() {
        if (this.refs.moveVenue.getSelectedValue()) {
            Actions.moveToVenue(this.state.pendingOrder, this.refs.moveVenue.getSelectedValue());
            this._clearPendingAction();
        }
    },

    _onTouchTapSync(order) {
        Actions.syncOrder(order);
    }
});
export default MainView;
