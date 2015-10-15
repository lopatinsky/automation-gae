import React from 'react';
import { OrderStore, VenuesStore, ClientStore, PaymentsStore, AddressStore } from '../stores';
import { OrderMenuItem, VenuesDialog, ClientInfoDialog, PaymentTypesDialog, CommentDialog } from '../components';
import { Navigation } from 'react-router';
import { List, ListItem, Card, CardText, RaisedButton, DatePicker, RadioButtonGroup, RadioButton, DropDownMenu, Snackbar, ListDivider }
    from 'material-ui';
import TimePickerDialog from 'material-ui/lib/time-picker/time-picker-dialog';
import DatePickerDialog from 'material-ui/lib/date-picker/date-picker-dialog';
import Actions from '../Actions';

const OrderScreen = React.createClass({
    mixins: [Navigation],

    _order() {
        Actions.order();
    },

    _refresh() {
        var orderId = OrderStore.getOrderId();
        if (orderId != null) {
            this.transitionTo('historyOrder', {
                order_id: orderId
            });
        }
        var slots = VenuesStore.getChosenDelivery().slots;
        if (slots.length > 0 && OrderStore.getSlotId() == null) {
            OrderStore.setSlotId(slots[0].id);
        }
        if (OrderStore.getOrderError() != null) {
            this.refs.orderSnackBar.show();
        }
        this.setState({});
    },

    _getServerInfo() {
        if (OrderStore.getErrors().length > 0) {
            return <div style={{padding: '12px 48px 0 36px', color: 'red'}}>
                {this._getErrors()}
            </div>
        } else {
            return <div>
                <div style={{padding: '12px 48px 0 36px'}}>
                    {this._getPromos()}
                </div>
                <div style={{padding: '12px 48px 0 36px'}}>
                    {this._getDeliveryDescription()}
                </div>
            </div>;
        }
    },

    _getPromos() {
        return OrderStore.getPromos().map(promo => {
            return <div>{promo.text + '\n'}</div>
        });
    },

    _getDeliveryDescription() {
        var delivery = VenuesStore.getChosenDelivery();
        if (delivery.id == 2 && OrderStore.getDeliverySumStr().length > 0) {
            return <div>
                {OrderStore.getDeliverySumStr()}
            </div>;
        } else {
            return '';
        }
    },

    _getErrors() {
        return OrderStore.getErrors().map(error => {
            return <div>{error + '\n'}</div>;
        });
    },

    _getTotalSum() {
        var menuTotalSum = OrderStore.getTotalSum();
        var validationTotalSum = OrderStore.getValidationTotalSum();
        var deliverySum = OrderStore.getDeliverySum();
        if (menuTotalSum != validationTotalSum + deliverySum) {
            return <div style={{textAlign: 'right', fontSize: '14px'}}>
                <b>
                    {'Итого: '}
                    <strike>{menuTotalSum + ' '}</strike>
                    {validationTotalSum + deliverySum}
                </b>
            </div>;
        } else {
            return <div style={{textAlign: 'right'}}>
                <b>
                    {'Итого: '}
                    {validationTotalSum + deliverySum}
                </b>
            </div>;
        }
    },

    _getItems() {
        var items = OrderStore.getItems();
        return items.map(item => {
            return (
                <OrderMenuItem item={item} />
            );
        });
    },

    _getOrderGifts() {
        var items = OrderStore.getOrderGifts();
        return items.map(item => {
            item.title += ' Подарок!';
            return (
                <OrderMenuItem item={item} />
            );
        });
    },

    _onMenuTap() {
        this.transitionTo('menu');
    },

    _onClientInfoTap() {
        this.refs.clientInfoDialog.show();
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
        this.transitionTo('address');
    },

    _onDeliveryTap(delivery) {
        VenuesStore.setChosenDelivery(delivery);
    },

    _onSlotTap(e, selectedIndex, menuItem) {
        OrderStore.setSlotId(menuItem.slot_id);
    },

    _getVenueInput() {
        var delivery = VenuesStore.getChosenDelivery();
        if (delivery.id == '2') {
            return <CardText onClick={this._onAddressTap}>{AddressStore.getAddressStr()}</CardText>
        } else {
            return <CardText onClick={this._onVenueTap}>{VenuesStore.getChosenVenue().title}</CardText>
        }
    },

    _setTime(time) {
        OrderStore.setTime(time);
    },

    _setDate(date) {
        OrderStore.setDay(date);
    },

    _getTimeInput() {
        var delivery = VenuesStore.getChosenDelivery();
        if (delivery.slots.length > 0) {
            var menuItems = delivery.slots.map(slot => {
                return { slot_id: slot.id, text: slot.name };
            });
            return <DropDownMenu
                menuItems={menuItems}
                selectedIndex={VenuesStore.getSlotIndex(OrderStore.getSlotId())}
                onChange={this._onSlotTap}/>;
        } else {
            return <div>
                <CardText onClick={() => this.refs.datePicker.show()}>
                    {OrderStore.getFullTimeStr()}
                </CardText>
                <DatePickerDialog
                    ref='datePicker'
                    onAccept={this._setDate}
                    onDismiss={() => this.refs.timePicker.show()}
                    hintText="Выберите дату"
                    autoOk={true} />
                <TimePickerDialog
                    ref='timePicker'
                    onAccept={this._setTime}
                    hintText="Выберитее время"
                    format="24hr"
                    autoOk={true} />
            </div>;
        }
    },

    _getDeliveryTypes() {
        var venue = VenuesStore.getChosenVenue();
        return venue.deliveries.map(delivery => {
            return (
                <RadioButton
                    label={delivery.name}
                    name={delivery.name}
                    value={delivery.name}
                    onClick={() => this._onDeliveryTap(delivery)}/>
            );
        });
    },

    componentDidMount() {
        VenuesStore.addChangeListener(this._refresh);
        OrderStore.addChangeListener(this._refresh);
        ClientStore.addChangeListener(this._refresh);
        PaymentsStore.addChangeListener(this._refresh);
        this._refresh();
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._refresh);
        OrderStore.removeChangeListener(this._refresh);
        ClientStore.removeChangeListener(this._refresh);
        PaymentsStore.removeChangeListener(this._refresh);
    },

    render() {
        return <div style={{padding: '64px 0 0 0'}}>
            {this._getItems()}
            {this._getOrderGifts()}
            <div>
                <RaisedButton
                    label='Меню'
                    onClick={this._onMenuTap}
                    style={{width: '93%', margin: '12px 12px 0 12px'}} />
            </div>
            <div style={{padding: '12px 24px 0 12px'}}>
                {this._getTotalSum()}
            </div>
            {this._getServerInfo()}
            <Card style={{width: '93%', margin: '12px 12px 0 12px'}}>
                <RadioButtonGroup
                    style={{margin: '12px'}}
                    name='group'
                    valueSelected={VenuesStore.getChosenDelivery().name}>
                    {this._getDeliveryTypes()}
                </RadioButtonGroup>
                <ListDivider/>
                {this._getVenueInput()}
                <ListDivider/>
                {this._getTimeInput()}
                <ListDivider/>
                <CardText onClick={this._onClientInfoTap}>{ClientStore.getRenderedInfo()}</CardText>
                <ListDivider/>
                <CardText onClick={this._onPaymentTypeTap}>{PaymentsStore.getChosenPaymentTypeTitle()}</CardText>
                <ListDivider/>
                <CardText onClick={this._onCommentTap}>{OrderStore.getRenderedComment()}</CardText>
            </Card>
            <VenuesDialog ref="venuesDialog"/>
            <ClientInfoDialog ref="clientInfoDialog"/>
            <PaymentTypesDialog ref="paymentTypesDialog"/>
            <CommentDialog ref="commentDialog" />
            <div>
                <RaisedButton
                    label='Заказать'
                    onClick={this._order}
                    style={{width: '93%', margin: '12px 12px 12px 12px'}} />
            </div>
            <Snackbar
                ref='orderSnackBar'
                message={OrderStore.getOrderError()}
                autoHideDuration='1000'
                onShow={Actions.checkOrder}
                onDismiss={() => {OrderStore.setOrderError(null)}}/>
        </div>;
    }
});

export default OrderScreen;