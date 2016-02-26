import React from 'react';
import { OrderStore, VenuesStore, ClientStore, PaymentsStore, AddressStore } from '../../stores';
import OrderMenuItem from './OrderMenuItem'
import { VenuesDialog, PaymentTypesDialog, CommentDialog, TimeSlotsDialog } from '../dialogs';
import { List, ListItem, Card, CardText, RaisedButton, DatePicker, RadioButtonGroup, RadioButton, DropDownMenu, Snackbar, Divider, FontIcon }
    from 'material-ui';
import TimePickerDialog from 'material-ui/lib/time-picker/time-picker-dialog';
import DatePickerDialog from 'material-ui/lib/date-picker/date-picker-dialog';
import { ServerRequests } from '../../actions';
import settings from '../../settings';

const OrderScreen = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _order() {
        ServerRequests.order();
    },

    _refresh() {
        var orderId = OrderStore.getOrderId();
        if (orderId != null) {
            this.context.router.push(`/order/${orderId}`);
        }
        var delivery = VenuesStore.getChosenDelivery();
        if (delivery) {
            var slots = delivery.slots;
            if (slots.length > 0 && OrderStore.slotId == null) {
                OrderStore.setSlotId(slots[0].id);
            }
        }
        this.setState({error: OrderStore.orderError});
    },

    _getServerInfo() {
        if (OrderStore.errors.length) {
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
        if (OrderStore.promos.length > 0) {
            return <div style={{padding: '12px 48px 0 36px'}}>
                {OrderStore.promos.map((promo, i) => {
                    return <div key={i}>{promo.text + '\n'}</div>
                })}
            </div>;
        } else {
            return null;
        }
    },

    _getDeliveryDescription() {
        var delivery = VenuesStore.getChosenDelivery();
        if (delivery && delivery.id == 2 && OrderStore.deliverySumStr.length > 0) {
            return <div style={{padding: '12px 48px 0 36px'}}>
                {OrderStore.deliverySumStr}
            </div>;
        } else {
            return null;
        }
    },

    _getErrors() {
        return OrderStore.errors.map((error, i) => {
            return <div key={i}>{error + '\n'}</div>;
        });
    },

    _getTotalSum() {
        var menuTotalSum = OrderStore.getTotalSum();
        const style = {textAlign: 'right'};
        if (menuTotalSum != OrderStore.validationSum + OrderStore.deliverySum) {
            return <div style={style}>
                Итого:{' '}
                <strike>{menuTotalSum}</strike>{' '}
                {OrderStore.validationSum + OrderStore.deliverySum}
            </div>;
        } else {
            return <div style={style}>
                Итого:{' '}
                {OrderStore.validationSum + OrderStore.deliverySum}
            </div>;
        }
    },

    _getItems() {
        return OrderStore.items.map((item, i) => {
            return (
                <OrderMenuItem key={i} item={item} />
            );
        });
    },

    _getOrderGifts() {
        return OrderStore.orderGifts.map((item, i) => {
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
        VenuesStore.setChosenDelivery(delivery);
    },

    _onSlotTap() {
        this.refs.timeSlotsDialog.show();
    },

    _getVenueInput() {
        var delivery = VenuesStore.getChosenDelivery();
        if (!delivery) {
            return <div/>;
        }
        if (delivery.id == '2') {
            return <ListItem
                        primaryText={AddressStore.getAddressStr()}
                        leftIcon={<FontIcon color={settings.primaryColor}
                                            className="material-icons">
                                      location_on
                                  </FontIcon>}
                        onClick={this._onAddressTap}>
            </ListItem>;
        } else {
            return <ListItem
                        primaryText={VenuesStore.getChosenVenue().title}
                        leftIcon={<FontIcon color={settings.primaryColor}
                                            className="material-icons">
                                      location_on
                                  </FontIcon>}
                        onClick={this._onVenueTap}>
            </ListItem>;
        }
    },

    _setTime(time) {
        OrderStore.setTime(time);
    },

    _setDate(date) {
        OrderStore.setDay(date);
        this.refs.timePicker.show();
    },

    _getTimeInput() {
        var delivery = VenuesStore.getChosenDelivery();
        if (!delivery) {
            return null;
        }
        if (delivery.slots.length > 0) {
            var slot = VenuesStore.getSlot(OrderStore.slotId);
            if (slot == null) {
                slot = {
                    name: 'Загружается...'
                }
            }
            return <ListItem
                        primaryText={slot.name}
                        leftIcon={<FontIcon color={settings.primaryColor}
                                            className="material-icons">
                                      schedule
                                  </FontIcon>}
                        onClick={this._onSlotTap}/>;
        } else {
            return <div>
                <ListItem
                        primaryText={OrderStore.getFullTimeStr()}
                        leftIcon={<FontIcon color={settings.primaryColor}
                                            className="material-icons">
                                      schedule
                                  </FontIcon>}
                        onClick={() => this.refs.datePicker.show()}>
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
        }
    },

    _getDeliveryTypes() {
        var venue = VenuesStore.getChosenVenue();
        if (venue) {
            return venue.deliveries.map(delivery => {
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
        return <ListItem
                    primaryText={ClientStore.getRenderedInfo()}
                    leftIcon={<FontIcon color={settings.primaryColor}
                                        className="material-icons">
                                  perm_identity
                              </FontIcon>}
                    onClick={this._onClientInfoTap}/>;
    },

    _getPaymentType() {
        let pt = OrderStore.chosenPaymentType,
            title = pt ? pt.really_title : 'Выберите способ оплаты';
        return <ListItem
                    primaryText={title}
                    leftIcon={<FontIcon color={settings.primaryColor}
                                        className="material-icons">
                                  account_balance_wallet
                              </FontIcon>}
                    onClick={this._onPaymentTypeTap}/>;
    },

    _getComment() {
        const comment = OrderStore.comment,
            style = comment ? {} : {color: '#bbbbbb'};
        return <ListItem
                    primaryText={comment ? comment : 'Комментарий'}
                    style={style}
                    leftIcon={<FontIcon color={settings.primaryColor}
                                        className="material-icons">
                                comment
                              </FontIcon>}
                    onClick={this._onCommentTap}/>;
    },

    componentDidMount() {
        this._refresh();
        ServerRequests.checkOrder();
        VenuesStore.addChangeListener(this._refresh);
        OrderStore.addChangeListener(this._refresh);
        ClientStore.addChangeListener(this._refresh);
        PaymentsStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._refresh);
        OrderStore.removeChangeListener(this._refresh);
        ClientStore.removeChangeListener(this._refresh);
        PaymentsStore.removeChangeListener(this._refresh);
    },

    getInitialState() {
        return {
            error: null
        };
    },

    render() {
        var delivery = VenuesStore.getChosenDelivery();
        return <div style={{padding: '64px 0 0 0'}}>
            {this._getItems()}
            {this._getOrderGifts()}
            <div style={{margin: '12px 12px 0 12px'}}>
                <RaisedButton
                    labelStyle={{color: settings.primaryColor}}
                    label='Меню'
                    onClick={this._onMenuTap}
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
            <TimeSlotsDialog ref="timeSlotsDialog"/>
            <div style={{width: '100%', position: 'fixed', bottom: '0px' }}>
                <RaisedButton
                    primary={true}
                    label='Заказать'
                    onClick={this._order}
                    style={{display: 'block', margin: '0 12px 12px'}} />
            </div>
            <Snackbar
                ref='orderSnackBar'
                style={{padding: '6px', width: '100%', marginLeft: '0', bottom: '0', textAlign: 'center', maxHeight: '128px', height: null, lineHeight: '175%'}}
                message={this.state.error || ''}
                autoHideDuration={5000}
                open={!! this.state.error}
                onRequestClose={() => {this.setState({error: null}); OrderStore.setOrderError(null)}}/>
        </div>;
    }
});

export default OrderScreen;