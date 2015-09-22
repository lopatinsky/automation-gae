import React from 'react';
import { OrderStore, VenuesStore, ClientStore, PaymentsStore, AddressStore } from '../stores';
import { OrderMenuItem, VenuesDialog, ClientInfoDialog, PaymentTypesDialog } from '../components';
import { Navigation } from 'react-router';
import { List, ListItem, Card, CardText, FlatButton, TimePicker, DatePicker, RadioButtonGroup, RadioButton, DropDownMenu } from 'material-ui';
import Actions from '../Actions';

const OrderScreen = React.createClass({
    mixins: [Navigation],

    _order() {
        Actions.checkOrder();
    },

    _refresh() {
        this.setState({});
    },

    _getItems() {
        var items = OrderStore.getItems();
        return items.map(item => {
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
            return <ListItem
                        primaryText={AddressStore.getAddressStr()}
                        onClick={this._onAddressTap}/>
        } else {
            return <ListItem
                        primaryText={VenuesStore.getChosenVenue().title}
                        onClick={this._onVenueTap}/>
        }
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
                <DatePicker
                    hintText="Выберите дату"
                    autoOk={true} />
                <TimePicker
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
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._refresh);
        OrderStore.removeChangeListener(this._refresh);
        ClientStore.removeChangeListener(this._refresh);
        PaymentsStore.removeChangeListener(this._refresh);
    },

    render() {
        return <div>
            {this._getItems()}
            Итого: {OrderStore.getTotalSum()}
            <Card onClick={this._onMenuTap}>
                <CardText>Меню</CardText>
            </Card>
            <RadioButtonGroup name='group'>
                {this._getDeliveryTypes()}
            </RadioButtonGroup>
            <List>
                {this._getVenueInput()}
            </List>
            <Card onClick={this._onClientInfoTap}>
                <CardText>{ClientStore.getName()}</CardText>
            </Card>
            <Card onClick={this._onPaymentTypeTap}>
                <CardText>{PaymentsStore.getChosenPaymentType().title}</CardText>
            </Card>
            {this._getTimeInput()}
            <VenuesDialog ref="venuesDialog"/>
            <ClientInfoDialog ref="clientInfoDialog"/>
            <PaymentTypesDialog ref="paymentTypesDialog"/>
            <FlatButton label='Заказать' onClick={this._order} />
        </div>;
    }
});

export default OrderScreen;