import React from 'react';
import { OrderStore, VenuesStore } from '../stores';
import { OrderMenuItem, VenuesDialog } from '../components';
import { Navigation } from 'react-router';
import { List, ListItem, Card, CardText, FlatButton, TimePicker, DatePicker, RadioButtonGroup, RadioButton } from 'material-ui';

const OrderScreen = React.createClass({
    mixins: [Navigation],

    _order() {
        return 1;
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

    _onVenueTap() {
        this.refs.venuesDialog.show();
    },

    _onAddressTap() {
        alert('Address tap');
    },

    _onDeliveryTap(delivery) {
        VenuesStore.setChosenDelivery(delivery);
    },

    _getVenueInput() {
        var delivery = VenuesStore.getChosenDelivery();
        if (delivery.id == '2') {
            return <ListItem
                        primaryText={'Введите адрес'}
                        onClick={this._onAddressTap}/>
        } else {
            return <ListItem
                        primaryText={VenuesStore.getChosenVenue().title}
                        onClick={this._onVenueTap}/>
        }
    },

    _getTimeInput() {
        var venue = VenuesStore.getChosenVenue();
        return <div>
            <DatePicker
                hintText="Выберите дату"
                autoOk={true} />
            <TimePicker
                hintText="Выберитее время"
                format="24hr"
                autoOk={true} />
        </div>;
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
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._refresh);
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

            <VenuesDialog ref="venuesDialog"/>
            <FlatButton label='Заказать' onClick={this._order} />
        </div>;
    }
});

export default OrderScreen;