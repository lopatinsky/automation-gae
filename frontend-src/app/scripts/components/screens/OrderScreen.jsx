import React from 'react';
import moment from 'moment';
import { OrderStore, ClientStore, PaymentsStore, AddressStore, CompanyStore } from '../../stores';
import OrderMenuItem from './OrderMenuItem'
import { VenuesDialog, PaymentTypesDialog, CommentDialog, TimeSlotsDialog } from '../dialogs';
import { List, ListItem, Card, CardText, RaisedButton, DatePicker, RadioButtonGroup, RadioButton, DropDownMenu, Snackbar, Divider, FontIcon }
    from 'material-ui';
import TimePickerDialog from 'material-ui/lib/time-picker/time-picker-dialog';
import DatePickerDialog from 'material-ui/lib/date-picker/date-picker-dialog';
import { AppActions, ServerRequests } from '../../actions';
import settings from '../../settings';

const OrderScreen = React.createClass({
    _pendingDate: null,

    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _order() {
        ServerRequests.order();
    },

    _stateFromOrderStore() {
        return {
            chosenDeliveryType: OrderStore.chosenDeliveryType,
            chosenVenue: OrderStore.chosenVenue,
            chosenPaymentType: OrderStore.chosenPaymentType,
            chosenTime: OrderStore.chosenTime,
            comment: OrderStore.comment,

            items: OrderStore.items,
            orderGifts: OrderStore.orderGifts,

            menuTotalSum: OrderStore.getTotalSum(),
            validationSum: OrderStore.validationSum,
            deliverySum: OrderStore.deliverySum,
            deliverySumStr: OrderStore.deliverySumStr,

            errors: OrderStore.errors,
            promos: OrderStore.promos
        };
    },

    _onOrderStoreChanged(data) {
        data = data || {};
        var orderId = data.orderId;
        if (orderId != null) {
            this.context.router.push(`/order/${orderId}`);
        }
        if (data.orderError) {
            this.setState({
                orderError: data.orderError
            })
        }
        this.setState(this._stateFromOrderStore());
        if (data.checkOrder) {
            setImmediate(ServerRequests.checkOrder);
        }
    },

    getInitialState() {
        return {
            orderError: null,
            ...this._stateFromOrderStore()
        };
    },

    _getServerInfo() {
        if (this.state.errors.length) {
            return <div style={{padding: '12px 48px 0 36px', color: 'red'}}>
                {this._getErrors()}
            </div>
        } else {
            return <div>
                {this._getPromos()}
                {this._getDeliveryDescription()}
            </div>;
        }
    },

    _getPromos() {
        if (this.state.promos.length > 0) {
            return <div style={{padding: '12px 48px 0 36px'}}>
                {this.state.promos.map((promo, i) => {
                    return <div key={i}>{promo.text + '\n'}</div>
                })}
            </div>;
        } else {
            return null;
        }
    },

    _getDeliveryDescription() {
        var delivery = this.state.chosenDeliveryType;
        if (delivery && delivery.id == 2 && this.state.deliverySumStr) {
            return <div style={{padding: '12px 48px 0 36px'}}>
                {this.state.deliverySumStr}
            </div>;
        } else {
            return null;
        }
    },

    _getErrors() {
        return this.state.errors.map((error, i) => {
            return <div key={i}>{error + '\n'}</div>;
        });
    },

    _getTotalSum() {
        const style = {textAlign: 'right'};
        if (this.state.menuTotalSum != this.state.validationSum + this.state.deliverySum) {
            return <div style={style}>
                Итого:{' '}
                <strike>{this.state.menuTotalSum}</strike>{' '}
                {this.state.validationSum + this.state.deliverySum}
            </div>;
        } else {
            return <div style={style}>
                Итого: {this.state.menuTotalSum}
            </div>;
        }
    },

    _getItems() {
        return this.state.items.map((item, i) => {
            return (
                <OrderMenuItem key={i} item={item} />
            );
        });
    },

    _getOrderGifts() {
        return this.state.orderGifts.map((item, i) => {
            return (
                <OrderMenuItem key={i} item={item} gift={true} />
            );
        });
    },

    _onMenuTap() {
        this.context.router.replace('/menu');
    },

    _onClientInfoTap() {
        this.context.router.push('/profile');
    },

    _onPaymentTypeTap() {
        this.refs.paymentTypesDialog.show();
    },

    _onVenueTap() {
        this.refs.venuesDialog.show();
    },

    _onCommentTap() {
        this.refs.commentDialog.show();
    },

    _onAddressTap() {
        this.context.router.push('/address');
    },

    _onDeliveryTap(delivery) {
        AppActions.setDeliveryType(delivery);
    },

    _onSlotTap() {
        this.refs.timeSlotsDialog.show();
    },

    _onSlotChosen(slotId) {
        const timeObj = {slotId};
        if (this.state.chosenDeliveryType.mode == 2) {
            timeObj.picker = moment(this._pendingDate)
                .set({
                    hour: 0,
                    minute: 0,
                    second: 0,
                    millisecond: 0
                });
        }
        AppActions.setTime(timeObj)
    },

    _getVenueInput() {
        var delivery = this.state.chosenDeliveryType;
        if (!delivery) {
            return null;
        }
        if (delivery.id == '2') {
            return <ListItem
                        primaryText={AddressStore.getAddressStr()}
                        leftIcon={<FontIcon color={settings.primaryColor}
                                            className="material-icons">
                                      location_on
                                  </FontIcon>}
                        onTouchTap={this._onAddressTap}>
            </ListItem>;
        } else {
            if (!this.state.chosenVenue) {
                return null;
            }
            return <ListItem
                        primaryText={this.state.chosenVenue.title}
                        leftIcon={<FontIcon color={settings.primaryColor}
                                            className="material-icons">
                                      location_on
                                  </FontIcon>}
                        onTouchTap={this._onVenueTap}>
            </ListItem>;
        }
    },

    _setTime(time) {
        const deliveryTime = moment(this._pendingDate)
            .set({
                hour: time.getHours(),
                minute: time.getMinutes(),
                second: 0,
                millisecond: 0
            });
        AppActions.setTime({
            picker: deliveryTime
        });
    },

    _setDate(date) {
        this._pendingDate = date;
        if (this.state.chosenDeliveryType.mode == 1) {
            this.refs.timePicker.show();
        } else {
            this.refs.timeSlotsDialog.show();
        }
    },

    _getTimeInput() {
        var delivery = this.state.chosenDeliveryType;
        if (!delivery) {
            return null;
        }
        if (delivery.mode == 0 || delivery.mode == 3) {
            let text, style = {};
            if (this.state.chosenTime) {
                text = CompanyStore.getSlot(delivery, this.state.chosenTime.slotId).name;
            } else {
                text = 'Выберите время';
                style = {color: settings.errorColor};
            }
            return <ListItem style={style}
                             primaryText={text}
                             leftIcon={<FontIcon color={settings.primaryColor}
                                                 className="material-icons">
                                           schedule
                                       </FontIcon>}
                             onTouchTap={this._onSlotTap}/>;
        } else if (delivery.mode == 1) {
            let timeStr, style = {};
            if (this.state.chosenTime) {
                timeStr = this.state.chosenTime.picker.format("D.MM, H:mm");
            } else {
                timeStr = 'Выберите время';
                style = {
                    color: settings.errorColor
                };
            }
            return <div>
                <ListItem style={style}
                          primaryText={timeStr}
                          leftIcon={<FontIcon color={settings.primaryColor}
                                              className="material-icons">
                                        schedule
                                    </FontIcon>}
                          onTouchTap={() => this.refs.datePicker.show()}>
                </ListItem>
                <DatePickerDialog
                    ref='datePicker'
                    onAccept={this._setDate}
                    hintText="Выберите дату" />
                <TimePickerDialog
                    ref='timePicker'
                    onAccept={this._setTime}
                    hintText="Выберите время"
                    format="24hr" />
            </div>;
        } else if (delivery.mode == 2) {
            const {picker, slotId} = this.state.chosenTime,
                slot = CompanyStore.getSlot(delivery, slotId);
            let timeStr, style = {};
            if (picker && slot) {
                timeStr = `${time.format("D.MM")} ${slot.name}`;
                return <div>
                <ListItem style={style}
                          primaryText={timeStr}
                          leftIcon={<FontIcon color={settings.primaryColor}
                                              className="material-icons">
                                        schedule
                                    </FontIcon>}
                          onTouchTap={() => this.refs.datePicker.show()}>
                </ListItem>
                <DatePickerDialog
                    ref='datePicker'
                    onAccept={this._setDate}
                    hintText="Выберите дату" />
            </div>;
            }
        }
    },

    _getDeliveryTypes() {
        const deliveryTypes = CompanyStore.getDeliveryTypes();
        if (deliveryTypes.length) {
            return deliveryTypes.map(delivery => {
                return (
                    <RadioButton key={delivery.id}
                                 label={delivery.name}
                                 name={delivery.name}
                                 value={delivery.id}
                                 onTouchTap={() => this._onDeliveryTap(delivery)}/>
                );
            });
        } else {
            return null;
        }
    },

    _getClientInfo() {
        let text, style = {},
            name = ClientStore.getName(),
            phone = ClientStore.getPhone();
        if (!name) {
            text = 'Представьтесь, пожалуйста';
            style = {color: settings.errorColor};
        } else if (!phone) {
            text = 'Введите номер телефона';
            style = {color: settings.errorColor};
        } else {
            text = name;
        }
        return <ListItem
                    primaryText={text}
                    style={style}
                    leftIcon={<FontIcon color={settings.primaryColor}
                                        className="material-icons">
                                  perm_identity
                              </FontIcon>}
                    onTouchTap={this._onClientInfoTap}/>;
    },

    _getPaymentType() {
        let pt = this.state.chosenPaymentType,
            title = pt ? pt.really_title : 'Выберите способ оплаты';
        return <ListItem
                    primaryText={title}
                    leftIcon={<FontIcon color={settings.primaryColor}
                                        className="material-icons">
                                  account_balance_wallet
                              </FontIcon>}
                    onTouchTap={this._onPaymentTypeTap}/>;
    },

    _getComment() {
        const comment = this.state.comment,
            style = comment ? {} : {color: '#bbbbbb'};
        return <ListItem
                    primaryText={comment ? comment : 'Комментарий'}
                    style={style}
                    leftIcon={<FontIcon color={settings.primaryColor}
                                        className="material-icons">
                                comment
                              </FontIcon>}
                    onTouchTap={this._onCommentTap}/>;
    },

    componentDidMount() {
        ServerRequests.checkOrder()
        OrderStore.addChangeListener(this._onOrderStoreChanged);
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this._onOrderStoreChanged);
    },

    render() {
        var delivery = this.state.chosenDeliveryType;
        return <div style={{padding: '64px 0 0 0'}}>
            {this._getItems()}
            {this._getOrderGifts()}
            <div style={{margin: '12px 12px 0 12px'}}>
                <RaisedButton
                    labelStyle={{color: settings.primaryColor}}
                    label='Меню'
                    onTouchTap={this._onMenuTap}
                    style={{width: '100%'}} />
            </div>
            <div style={{padding: '12px 24px 0 12px'}}>
                {this._getTotalSum()}
            </div>
            {this._getServerInfo()}
            <div style={{width: '100%'}}>
                <Card style={{margin: '12px 12px 60px 12px'}}>
                    <RadioButtonGroup style={{margin: '12px'}}
                                      name='group'
                                      valueSelected={delivery ? delivery.id : null}>
                        {this._getDeliveryTypes()}
                    </RadioButtonGroup>
                    <Divider/>
                    <List style={{paddingBottom: '0', paddingTop: '0'}}>
                        {this._getVenueInput()}
                        <Divider/>
                        {this._getTimeInput()}
                        <Divider/>
                        {this._getClientInfo()}
                        <Divider/>
                        {this._getPaymentType()}
                        <Divider/>
                        {this._getComment()}
                    </List>
                </Card>
            </div>
            <VenuesDialog ref="venuesDialog"/>
            <PaymentTypesDialog ref="paymentTypesDialog"/>
            <CommentDialog ref="commentDialog"/>
            <TimeSlotsDialog ref="timeSlotsDialog" onSlotChosen={this._onSlotChosen}/>
            <div style={{width: '100%', position: 'fixed', bottom: '0px' }}>
                <RaisedButton
                    primary={true}
                    label='Заказать'
                    onTouchTap={this._order}
                    style={{display: 'block', margin: '0 12px 12px'}} />
            </div>
            <Snackbar
                ref='orderSnackBar'
                style={{padding: '6px', width: '100%', marginLeft: '0', bottom: '0', textAlign: 'center', maxHeight: '128px', height: null, lineHeight: '175%'}}
                message={this.state.orderError || ''}
                autoHideDuration={5000}
                open={!! this.state.orderError}
                onRequestClose={() => {this.setState({error: null}); OrderStore.setOrderError(null)}}/>
        </div>;
    }
});

export default OrderScreen;